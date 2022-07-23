import logging
from datetime import datetime, timedelta
from threading import Lock
from typing import Optional

import pytz
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job

from homecon.core.event import Event
from homecon.core.states.state import State, IStateManager
from homecon.plugins.shading.calculator import IShadingPositionCalculator, IWantedHeatGainCalculator, ICloudCoverCalculator, IRainCalculator
from homecon.plugins.shading.domain import StateBasedShading


logger = logging.getLogger(__name__)


class ShadingController:

    SHADING_STATE_TYPE = 'shading'
    POSITION_STATE = 'position'
    MINIMUM_POSITION_STATE = 'minimum_position'
    MAXIMUM_POSITION_STATE = 'maximum_position'
    CONTROLLER_OVERRIDE_STATE = 'controller_override'
    EVENT_SOURCE = 'shading_controller'

    def __init__(self,
                 state_manager: IStateManager,
                 wanted_heat_gain_calculator: IWantedHeatGainCalculator,
                 wanted_heat_gain_state: State,
                 cloud_cover_calculator: ICloudCoverCalculator,
                 cloud_cover_state: State,
                 rain_calculator: IRainCalculator,
                 position_calculator: IShadingPositionCalculator,
                 longitude_state: State, latitude_state: State, elevation_state: State,
                 interval: int = 1800, override_duration: int = 4 * 3600):
        self._state_manager = state_manager
        self._wanted_heat_gain_calculator = wanted_heat_gain_calculator
        self._wanted_heat_gain_state = wanted_heat_gain_state

        self._cloud_cover_calculator = cloud_cover_calculator
        self._cloud_cover_state = cloud_cover_state

        self._rain_calculator = rain_calculator

        self._position_calculator = position_calculator

        self._longitude_state = longitude_state
        self._latitude_state = latitude_state
        self._elevation_state = elevation_state
        self._override_duration = override_duration
        self._interval = interval

        executors = {
            'default': ThreadPoolExecutor(5),
        }
        job_defaults = {
            'coalesce': True,
            'max_instances': 3,
            'misfire_grace_time': 3600
        }
        self.scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)

        self._run_job: Optional[Job] = None
        self._run_job_lock = Lock()
        self._reset_jobs = {}

    def start(self):
        self.scheduler.start()
        self.schedule_run(30)
        logger.info('started shading controller')

    def stop(self):
        self.scheduler.shutdown(wait=False)

    def _get_shading_from_state(self, state: State, rain: bool) -> StateBasedShading:
        position_state = None
        minimum_position_state = None
        maximum_position_state = None
        controller_override_state = None

        for child in state.children:
            if child.name == self.POSITION_STATE:
                position_state = child
            if child.name == self.MINIMUM_POSITION_STATE:
                minimum_position_state = child
            if child.name == self.MAXIMUM_POSITION_STATE:
                maximum_position_state = child
            if child.name == self.CONTROLLER_OVERRIDE_STATE:
                controller_override_state = child

        # add missing states
        if position_state is None:
            position_state = self._state_manager.add(self.POSITION_STATE, parent=state, type='float', quantity='Position', unit='-', value=0.)
        if minimum_position_state is None:
            minimum_position_state = self._state_manager.add(self.MINIMUM_POSITION_STATE,
                                                             parent=state, type='float', quantity='Position', unit='-', value=0.)
        if maximum_position_state is None:
            maximum_position_state = self._state_manager.add(self.MAXIMUM_POSITION_STATE,
                                                             parent=state, type='float', quantity='Position', unit='-', value=1.)
        if controller_override_state is None:
            controller_override_state = self._state_manager.add(self.CONTROLLER_OVERRIDE_STATE, parent=state, type='bool', value=0)

        override_when_raining = state.config.get('override_when_raining', 0) == 1 and rain

        return StateBasedShading(
            name=state.path,
            position=position_state.value,
            set_position=lambda x: position_state.set_value(x, source=self.EVENT_SOURCE),
            minimum_position=minimum_position_state.value
            if minimum_position_state is not None and minimum_position_state.value is not None else None,
            maximum_position=maximum_position_state.value
            if maximum_position_state is not None and maximum_position_state.value is not None else None,
            controller_override=controller_override_state.value == 1 or override_when_raining
            if controller_override_state is not None and controller_override_state.value is not None else False,
            area=state.config.get('area', 1.0),
            transparency=state.config.get('transparency', 0.0),
            azimuth=state.config.get('azimuth', 0.0),
            tilt=state.config.get('tilt', 90.0),
            longitude=self._longitude_state.value or 0.0,
            latitude=self._latitude_state.value or 0.0,
            elevation=self._elevation_state.value or 0.0,
            horizon_solar_altitude=state.config.get('horizon_solar_altitude', 5.0),
            direct_irradiation_coefficient=state.config.get('direct_irradiation_coefficient', 1.0),
            diffuse_irradiation_coefficient=state.config.get('diffuse_irradiation_coefficient', 0.5),
            ground_irradiation_coefficient=state.config.get('ground_irradiation_coefficient', 0.0),
        )

    def set_override(self, state: State):
        for child in state.children:
            if child.name == self.CONTROLLER_OVERRIDE_STATE:
                logger.debug(f'setting override for {state} to {child}')
                child.set_value(1)

                try:
                    old_job = self._reset_jobs.pop(child.path)
                except KeyError:
                    pass
                else:
                    old_job.remove()
                job = self.scheduler.add_job(self.reset_override,
                                             trigger=DateTrigger(datetime.now() + timedelta(seconds=self._override_duration)), args=(child,))
                self._reset_jobs[child.path] = job

    def reset_override(self, child: State):
        child.set_value(0)
        logger.debug(f'resetting override for {child.parent}')

        try:
            self._reset_jobs.pop(child.path)
        except KeyError:
            pass

    def run(self):
        logger.info('running shading controller')
        with self._run_job_lock:
            if self._run_job is not None:
                try:
                    self._run_job.remove()
                except JobLookupError:
                    pass
            self._run_job = self.scheduler.add_job(self.run, trigger=DateTrigger(datetime.now() + timedelta(seconds=self._interval)))

        rain = self._rain_calculator.calculate_rain()

        shadings = []
        for state in self._state_manager.all():
            if state.type == self.SHADING_STATE_TYPE:
                logger.debug(f'creating shading object for state {state}')
                shadings.append(self._get_shading_from_state(state, rain))

        wanted_heat_gain = self._wanted_heat_gain_calculator.calculate_wanted_heat_gain()
        logger.debug(f'calculated wanted heat gain: {wanted_heat_gain:.0f} W')
        self._wanted_heat_gain_state.set_value(wanted_heat_gain)

        cloud_cover = self._cloud_cover_calculator.calculate_cloud_cover()
        logger.debug(f'calculated cloud cover: {cloud_cover:.2f}')
        self._cloud_cover_state.set_value(cloud_cover)

        positions = self._position_calculator.get_positions(shadings, wanted_heat_gain, cloud_cover)
        logger.info(f'calculated positions: {positions}')

        for shading, position in zip(shadings, positions):
            shading.set_position(position)

    @staticmethod
    def _job_is_scheduled(job: Job, threshold: float):
        now = datetime.now(tz=pytz.UTC)
        try:
            next_run_time = job.next_run_time
        except AttributeError:
            return False
        return job.next_run_time is not None and now <= next_run_time < now + timedelta(seconds=threshold)

    def schedule_run(self, interval: float):
        with self._run_job_lock:
            reschedule = True
            if self._run_job is not None:
                if self._job_is_scheduled(self._run_job, 5):
                    reschedule = False

                    logger.debug('controller already scheduled')
                else:
                    try:
                        self._run_job.remove()
                    except JobLookupError:
                        pass

            if reschedule:
                logger.debug('scheduled controller run in 5 seconds')
                self._run_job = self.scheduler.add_job(self.run, trigger=DateTrigger(datetime.now() + timedelta(seconds=interval)))

    def listen_state_value_changed(self, event: Event):
        state = event.data['state']
        if state.parent is not None and state.parent.type == self.SHADING_STATE_TYPE:
            if event.source != self.EVENT_SOURCE:
                if state.name == 'position':
                    if event.source == 'websocket':
                        self.set_override(state.parent)
                elif event.data['old'] != event.data['new']:
                    self.schedule_run(5)
