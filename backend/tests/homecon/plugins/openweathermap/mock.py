from homecon.plugins.openweathermap.openweathermap import IOpenWeatherMapApiClient


class MockOpenWeatherMapApiClient(IOpenWeatherMapApiClient):
    def get_forecast(self, api_key: str, longitude: float, latitude: float) -> dict:
        return {
            "lat": 51.05,
            "lon": 5.58,
            "timezone": "Europe/Brussels",
            "timezone_offset": 3600,
            "current": {
                "dt": 1635968066,
                "sunrise": 1635921211,
                "sunset": 1635955733,
                "temp": 6.2,
                "feels_like": 6.2,
                "pressure": 1003,
                "humidity": 93,
                "dew_point": 5.15,
                "uvi": 0,
                "clouds": 90,
                "visibility": 550,
                "wind_speed": 0.51,
                "wind_deg": 0,
                "weather": [
                    {
                        "id": 701,
                        "main": "Mist",
                        "description": "mist",
                        "icon": "50n"
                    }
                ]
            },
            "hourly": [
                {
                    "dt": 1635966000,
                    "temp": 6.18,
                    "feels_like": 5.5,
                    "pressure": 1003,
                    "humidity": 93,
                    "dew_point": 5.13,
                    "uvi": 0,
                    "clouds": 91,
                    "visibility": 10000,
                    "wind_speed": 1.34,
                    "wind_deg": 287,
                    "wind_gust": 1.36,
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1635969600,
                    "temp": 6.2,
                    "feels_like": 6.2,
                    "pressure": 1003,
                    "humidity": 93,
                    "dew_point": 5.15,
                    "uvi": 0,
                    "clouds": 90,
                    "visibility": 10000,
                    "wind_speed": 1.18,
                    "wind_deg": 274,
                    "wind_gust": 1.23,
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1635973200,
                    "temp": 6.02,
                    "feels_like": 5.05,
                    "pressure": 1003,
                    "humidity": 94,
                    "dew_point": 5.13,
                    "uvi": 0,
                    "clouds": 91,
                    "visibility": 10000,
                    "wind_speed": 1.55,
                    "wind_deg": 274,
                    "wind_gust": 1.54,
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1635976800,
                    "temp": 5.64,
                    "feels_like": 4.26,
                    "pressure": 1003,
                    "humidity": 94,
                    "dew_point": 4.75,
                    "uvi": 0,
                    "clouds": 89,
                    "visibility": 10000,
                    "wind_speed": 1.86,
                    "wind_deg": 272,
                    "wind_gust": 1.89,
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1635980400,
                    "temp": 5.11,
                    "feels_like": 4.05,
                    "pressure": 1004,
                    "humidity": 95,
                    "dew_point": 4.38,
                    "uvi": 0,
                    "clouds": 81,
                    "visibility": 10000,
                    "wind_speed": 1.52,
                    "wind_deg": 263,
                    "wind_gust": 1.51,
                    "weather": [
                        {
                            "id": 803,
                            "main": "Clouds",
                            "description": "broken clouds",
                            "icon": "04n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1635984000,
                    "temp": 4.55,
                    "feels_like": 3.42,
                    "pressure": 1004,
                    "humidity": 95,
                    "dew_point": 3.82,
                    "uvi": 0,
                    "clouds": 71,
                    "visibility": 10000,
                    "wind_speed": 1.51,
                    "wind_deg": 242,
                    "wind_gust": 1.53,
                    "weather": [
                        {
                            "id": 803,
                            "main": "Clouds",
                            "description": "broken clouds",
                            "icon": "04n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1635987600,
                    "temp": 3.97,
                    "feels_like": 2.02,
                    "pressure": 1005,
                    "humidity": 96,
                    "dew_point": 3.46,
                    "uvi": 0,
                    "clouds": 24,
                    "visibility": 10000,
                    "wind_speed": 2.14,
                    "wind_deg": 242,
                    "wind_gust": 2.61,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1635991200,
                    "temp": 3.68,
                    "feels_like": 1.89,
                    "pressure": 1005,
                    "humidity": 96,
                    "dew_point": 3.22,
                    "uvi": 0,
                    "clouds": 21,
                    "visibility": 10000,
                    "wind_speed": 1.95,
                    "wind_deg": 241,
                    "wind_gust": 2.35,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1635994800,
                    "temp": 3.49,
                    "feels_like": 1.92,
                    "pressure": 1005,
                    "humidity": 96,
                    "dew_point": 3.01,
                    "uvi": 0,
                    "clouds": 22,
                    "visibility": 10000,
                    "wind_speed": 1.73,
                    "wind_deg": 253,
                    "wind_gust": 1.79,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1635998400,
                    "temp": 3.33,
                    "feels_like": 1.46,
                    "pressure": 1005,
                    "humidity": 96,
                    "dew_point": 2.86,
                    "uvi": 0,
                    "clouds": 20,
                    "visibility": 10000,
                    "wind_speed": 1.97,
                    "wind_deg": 236,
                    "wind_gust": 2,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636002000,
                    "temp": 3.15,
                    "feels_like": 0.69,
                    "pressure": 1005,
                    "humidity": 96,
                    "dew_point": 2.73,
                    "uvi": 0,
                    "clouds": 18,
                    "visibility": 10000,
                    "wind_speed": 2.52,
                    "wind_deg": 232,
                    "wind_gust": 3.69,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636005600,
                    "temp": 2.94,
                    "feels_like": 0.28,
                    "pressure": 1005,
                    "humidity": 97,
                    "dew_point": 2.54,
                    "uvi": 0,
                    "clouds": 18,
                    "visibility": 10000,
                    "wind_speed": 2.7,
                    "wind_deg": 230,
                    "wind_gust": 4.76,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0.01
                },
                {
                    "dt": 1636009200,
                    "temp": 2.9,
                    "feels_like": 0.08,
                    "pressure": 1006,
                    "humidity": 97,
                    "dew_point": 2.56,
                    "uvi": 0,
                    "clouds": 23,
                    "visibility": 10000,
                    "wind_speed": 2.88,
                    "wind_deg": 233,
                    "wind_gust": 5.95,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02d"
                        }
                    ],
                    "pop": 0.13
                },
                {
                    "dt": 1636012800,
                    "temp": 4.4,
                    "feels_like": 2.48,
                    "pressure": 1006,
                    "humidity": 94,
                    "dew_point": 3.63,
                    "uvi": 0.04,
                    "clouds": 31,
                    "visibility": 10000,
                    "wind_speed": 2.19,
                    "wind_deg": 236,
                    "wind_gust": 5.58,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "pop": 0.28,
                    "rain": {
                        "1h": 0.16
                    }
                },
                {
                    "dt": 1636016400,
                    "temp": 5.39,
                    "feels_like": 3,
                    "pressure": 1007,
                    "humidity": 93,
                    "dew_point": 4.44,
                    "uvi": 0.1,
                    "clouds": 52,
                    "visibility": 10000,
                    "wind_speed": 2.96,
                    "wind_deg": 214,
                    "wind_gust": 5.39,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "pop": 0.42,
                    "rain": {
                        "1h": 0.67
                    }
                },
                {
                    "dt": 1636020000,
                    "temp": 5.68,
                    "feels_like": 2.81,
                    "pressure": 1007,
                    "humidity": 95,
                    "dew_point": 5.09,
                    "uvi": 0.41,
                    "clouds": 64,
                    "visibility": 9464,
                    "wind_speed": 3.79,
                    "wind_deg": 201,
                    "wind_gust": 8.02,
                    "weather": [
                        {
                            "id": 501,
                            "main": "Rain",
                            "description": "moderate rain",
                            "icon": "10d"
                        }
                    ],
                    "pop": 0.65,
                    "rain": {
                        "1h": 1.65
                    }
                },
                {
                    "dt": 1636023600,
                    "temp": 6.25,
                    "feels_like": 3.76,
                    "pressure": 1006,
                    "humidity": 95,
                    "dew_point": 5.69,
                    "uvi": 0.54,
                    "clouds": 71,
                    "visibility": 10000,
                    "wind_speed": 3.38,
                    "wind_deg": 225,
                    "wind_gust": 8.66,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "pop": 0.81,
                    "rain": {
                        "1h": 0.91
                    }
                },
                {
                    "dt": 1636027200,
                    "temp": 7.31,
                    "feels_like": 4.98,
                    "pressure": 1006,
                    "humidity": 94,
                    "dew_point": 6.48,
                    "uvi": 0.55,
                    "clouds": 76,
                    "visibility": 10000,
                    "wind_speed": 3.48,
                    "wind_deg": 245,
                    "wind_gust": 8.13,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "pop": 0.81,
                    "rain": {
                        "1h": 0.12
                    }
                },
                {
                    "dt": 1636030800,
                    "temp": 8.09,
                    "feels_like": 6.38,
                    "pressure": 1006,
                    "humidity": 92,
                    "dew_point": 7.04,
                    "uvi": 0.7,
                    "clouds": 100,
                    "visibility": 10000,
                    "wind_speed": 2.76,
                    "wind_deg": 252,
                    "wind_gust": 6.92,
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04d"
                        }
                    ],
                    "pop": 0.48
                },
                {
                    "dt": 1636034400,
                    "temp": 8.5,
                    "feels_like": 8.5,
                    "pressure": 1007,
                    "humidity": 92,
                    "dew_point": 7.39,
                    "uvi": 0.43,
                    "clouds": 100,
                    "visibility": 10000,
                    "wind_speed": 0.99,
                    "wind_deg": 259,
                    "wind_gust": 3.78,
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04d"
                        }
                    ],
                    "pop": 0.52
                },
                {
                    "dt": 1636038000,
                    "temp": 8.72,
                    "feels_like": 7.84,
                    "pressure": 1008,
                    "humidity": 92,
                    "dew_point": 7.54,
                    "uvi": 0.19,
                    "clouds": 95,
                    "visibility": 10000,
                    "wind_speed": 1.85,
                    "wind_deg": 4,
                    "wind_gust": 3.81,
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04d"
                        }
                    ],
                    "pop": 0.49
                },
                {
                    "dt": 1636041600,
                    "temp": 6.62,
                    "feels_like": 4.18,
                    "pressure": 1009,
                    "humidity": 96,
                    "dew_point": 6.13,
                    "uvi": 0,
                    "clouds": 75,
                    "visibility": 10000,
                    "wind_speed": 3.42,
                    "wind_deg": 16,
                    "wind_gust": 6.55,
                    "weather": [
                        {
                            "id": 803,
                            "main": "Clouds",
                            "description": "broken clouds",
                            "icon": "04d"
                        }
                    ],
                    "pop": 0.37
                },
                {
                    "dt": 1636045200,
                    "temp": 5.31,
                    "feels_like": 3.05,
                    "pressure": 1010,
                    "humidity": 97,
                    "dew_point": 4.97,
                    "uvi": 0,
                    "clouds": 64,
                    "visibility": 10000,
                    "wind_speed": 2.77,
                    "wind_deg": 18,
                    "wind_gust": 5.86,
                    "weather": [
                        {
                            "id": 803,
                            "main": "Clouds",
                            "description": "broken clouds",
                            "icon": "04n"
                        }
                    ],
                    "pop": 0.33
                },
                {
                    "dt": 1636048800,
                    "temp": 4.71,
                    "feels_like": 3.1,
                    "pressure": 1011,
                    "humidity": 96,
                    "dew_point": 4.27,
                    "uvi": 0,
                    "clouds": 59,
                    "visibility": 10000,
                    "wind_speed": 1.93,
                    "wind_deg": 2,
                    "wind_gust": 2.94,
                    "weather": [
                        {
                            "id": 803,
                            "main": "Clouds",
                            "description": "broken clouds",
                            "icon": "04n"
                        }
                    ],
                    "pop": 0.26
                },
                {
                    "dt": 1636052400,
                    "temp": 4.56,
                    "feels_like": 3.67,
                    "pressure": 1012,
                    "humidity": 95,
                    "dew_point": 3.96,
                    "uvi": 0,
                    "clouds": 18,
                    "visibility": 10000,
                    "wind_speed": 1.34,
                    "wind_deg": 330,
                    "wind_gust": 1.43,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0.01
                },
                {
                    "dt": 1636056000,
                    "temp": 4.59,
                    "feels_like": 3.34,
                    "pressure": 1013,
                    "humidity": 94,
                    "dew_point": 3.85,
                    "uvi": 0,
                    "clouds": 19,
                    "visibility": 10000,
                    "wind_speed": 1.61,
                    "wind_deg": 267,
                    "wind_gust": 1.59,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0.01
                },
                {
                    "dt": 1636059600,
                    "temp": 4.67,
                    "feels_like": 2.75,
                    "pressure": 1014,
                    "humidity": 95,
                    "dew_point": 4.05,
                    "uvi": 0,
                    "clouds": 31,
                    "visibility": 10000,
                    "wind_speed": 2.23,
                    "wind_deg": 260,
                    "wind_gust": 2.66,
                    "weather": [
                        {
                            "id": 802,
                            "main": "Clouds",
                            "description": "scattered clouds",
                            "icon": "03n"
                        }
                    ],
                    "pop": 0.01
                },
                {
                    "dt": 1636063200,
                    "temp": 4.72,
                    "feels_like": 2.87,
                    "pressure": 1015,
                    "humidity": 96,
                    "dew_point": 4.3,
                    "uvi": 0,
                    "clouds": 39,
                    "visibility": 10000,
                    "wind_speed": 2.17,
                    "wind_deg": 256,
                    "wind_gust": 3.03,
                    "weather": [
                        {
                            "id": 802,
                            "main": "Clouds",
                            "description": "scattered clouds",
                            "icon": "03n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636066800,
                    "temp": 4.66,
                    "feels_like": 2.86,
                    "pressure": 1015,
                    "humidity": 97,
                    "dew_point": 4.28,
                    "uvi": 0,
                    "clouds": 43,
                    "visibility": 10000,
                    "wind_speed": 2.11,
                    "wind_deg": 252,
                    "wind_gust": 2.48,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10n"
                        }
                    ],
                    "pop": 0.2,
                    "rain": {
                        "1h": 0.12
                    }
                },
                {
                    "dt": 1636070400,
                    "temp": 5,
                    "feels_like": 3.15,
                    "pressure": 1015,
                    "humidity": 96,
                    "dew_point": 4.6,
                    "uvi": 0,
                    "clouds": 46,
                    "visibility": 10000,
                    "wind_speed": 2.22,
                    "wind_deg": 247,
                    "wind_gust": 3.1,
                    "weather": [
                        {
                            "id": 802,
                            "main": "Clouds",
                            "description": "scattered clouds",
                            "icon": "03n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636074000,
                    "temp": 4.73,
                    "feels_like": 2.64,
                    "pressure": 1016,
                    "humidity": 96,
                    "dew_point": 4.28,
                    "uvi": 0,
                    "clouds": 31,
                    "visibility": 10000,
                    "wind_speed": 2.43,
                    "wind_deg": 257,
                    "wind_gust": 3.48,
                    "weather": [
                        {
                            "id": 802,
                            "main": "Clouds",
                            "description": "scattered clouds",
                            "icon": "03n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636077600,
                    "temp": 4.53,
                    "feels_like": 2.63,
                    "pressure": 1017,
                    "humidity": 96,
                    "dew_point": 4.02,
                    "uvi": 0,
                    "clouds": 23,
                    "visibility": 10000,
                    "wind_speed": 2.19,
                    "wind_deg": 269,
                    "wind_gust": 2.99,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636081200,
                    "temp": 4.42,
                    "feels_like": 2.76,
                    "pressure": 1017,
                    "humidity": 95,
                    "dew_point": 3.85,
                    "uvi": 0,
                    "clouds": 19,
                    "visibility": 10000,
                    "wind_speed": 1.94,
                    "wind_deg": 265,
                    "wind_gust": 2.14,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636084800,
                    "temp": 4.39,
                    "feels_like": 2.55,
                    "pressure": 1018,
                    "humidity": 95,
                    "dew_point": 3.78,
                    "uvi": 0,
                    "clouds": 17,
                    "visibility": 10000,
                    "wind_speed": 2.1,
                    "wind_deg": 262,
                    "wind_gust": 2.23,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636088400,
                    "temp": 4.34,
                    "feels_like": 2.56,
                    "pressure": 1019,
                    "humidity": 95,
                    "dew_point": 3.69,
                    "uvi": 0,
                    "clouds": 16,
                    "visibility": 10000,
                    "wind_speed": 2.04,
                    "wind_deg": 263,
                    "wind_gust": 2.06,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636092000,
                    "temp": 4.33,
                    "feels_like": 2.5,
                    "pressure": 1019,
                    "humidity": 95,
                    "dew_point": 3.67,
                    "uvi": 0,
                    "clouds": 17,
                    "visibility": 10000,
                    "wind_speed": 2.08,
                    "wind_deg": 265,
                    "wind_gust": 2.09,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02n"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636095600,
                    "temp": 4.37,
                    "feels_like": 2.99,
                    "pressure": 1020,
                    "humidity": 95,
                    "dew_point": 3.7,
                    "uvi": 0,
                    "clouds": 15,
                    "visibility": 10000,
                    "wind_speed": 1.69,
                    "wind_deg": 259,
                    "wind_gust": 1.78,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02d"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636099200,
                    "temp": 5.78,
                    "feels_like": 4.98,
                    "pressure": 1021,
                    "humidity": 92,
                    "dew_point": 4.71,
                    "uvi": 0.14,
                    "clouds": 12,
                    "visibility": 10000,
                    "wind_speed": 1.39,
                    "wind_deg": 243,
                    "wind_gust": 1.84,
                    "weather": [
                        {
                            "id": 801,
                            "main": "Clouds",
                            "description": "few clouds",
                            "icon": "02d"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636102800,
                    "temp": 7.66,
                    "feels_like": 6.98,
                    "pressure": 1022,
                    "humidity": 86,
                    "dew_point": 5.59,
                    "uvi": 0.39,
                    "clouds": 10,
                    "visibility": 10000,
                    "wind_speed": 1.5,
                    "wind_deg": 252,
                    "wind_gust": 2.33,
                    "weather": [
                        {
                            "id": 800,
                            "main": "Clear",
                            "description": "clear sky",
                            "icon": "01d"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636106400,
                    "temp": 9.19,
                    "feels_like": 8.53,
                    "pressure": 1023,
                    "humidity": 81,
                    "dew_point": 6.25,
                    "uvi": 0.72,
                    "clouds": 10,
                    "visibility": 10000,
                    "wind_speed": 1.69,
                    "wind_deg": 265,
                    "wind_gust": 2.59,
                    "weather": [
                        {
                            "id": 800,
                            "main": "Clear",
                            "description": "clear sky",
                            "icon": "01d"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636110000,
                    "temp": 10.4,
                    "feels_like": 9.51,
                    "pressure": 1023,
                    "humidity": 77,
                    "dew_point": 6.74,
                    "uvi": 0.95,
                    "clouds": 9,
                    "visibility": 10000,
                    "wind_speed": 2.04,
                    "wind_deg": 282,
                    "wind_gust": 3.28,
                    "weather": [
                        {
                            "id": 800,
                            "main": "Clear",
                            "description": "clear sky",
                            "icon": "01d"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636113600,
                    "temp": 11.24,
                    "feels_like": 10.35,
                    "pressure": 1023,
                    "humidity": 74,
                    "dew_point": 6.87,
                    "uvi": 0.99,
                    "clouds": 9,
                    "visibility": 10000,
                    "wind_speed": 2.26,
                    "wind_deg": 298,
                    "wind_gust": 3.6,
                    "weather": [
                        {
                            "id": 800,
                            "main": "Clear",
                            "description": "clear sky",
                            "icon": "01d"
                        }
                    ],
                    "pop": 0
                },
                {
                    "dt": 1636117200,
                    "temp": 11.55,
                    "feels_like": 10.61,
                    "pressure": 1023,
                    "humidity": 71,
                    "dew_point": 6.66,
                    "uvi": 0.8,
                    "clouds": 26,
                    "visibility": 10000,
                    "wind_speed": 2.76,
                    "wind_deg": 310,
                    "wind_gust": 3.92,
                    "weather": [
                        {
                            "id": 802,
                            "main": "Clouds",
                            "description": "scattered clouds",
                            "icon": "03d"
                        }
                    ],
                    "pop": 0.48
                },
                {
                    "dt": 1636120800,
                    "temp": 11.36,
                    "feels_like": 10.48,
                    "pressure": 1024,
                    "humidity": 74,
                    "dew_point": 6.94,
                    "uvi": 0.48,
                    "clouds": 32,
                    "visibility": 10000,
                    "wind_speed": 2.79,
                    "wind_deg": 311,
                    "wind_gust": 4.1,
                    "weather": [
                        {
                            "id": 802,
                            "main": "Clouds",
                            "description": "scattered clouds",
                            "icon": "03d"
                        }
                    ],
                    "pop": 0.42
                },
                {
                    "dt": 1636124400,
                    "temp": 10.08,
                    "feels_like": 9.26,
                    "pressure": 1024,
                    "humidity": 81,
                    "dew_point": 7.08,
                    "uvi": 0.2,
                    "clouds": 28,
                    "visibility": 10000,
                    "wind_speed": 2.85,
                    "wind_deg": 321,
                    "wind_gust": 5.59,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "pop": 0.37,
                    "rain": {
                        "1h": 0.14
                    }
                },
                {
                    "dt": 1636128000,
                    "temp": 7.9,
                    "feels_like": 6.44,
                    "pressure": 1025,
                    "humidity": 91,
                    "dew_point": 6.58,
                    "uvi": 0,
                    "clouds": 27,
                    "visibility": 10000,
                    "wind_speed": 2.37,
                    "wind_deg": 319,
                    "wind_gust": 3.69,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "pop": 0.45,
                    "rain": {
                        "1h": 0.13
                    }
                },
                {
                    "dt": 1636131600,
                    "temp": 7.24,
                    "feels_like": 5.85,
                    "pressure": 1026,
                    "humidity": 92,
                    "dew_point": 6.06,
                    "uvi": 0,
                    "clouds": 38,
                    "visibility": 10000,
                    "wind_speed": 2.14,
                    "wind_deg": 307,
                    "wind_gust": 2.85,
                    "weather": [
                        {
                            "id": 802,
                            "main": "Clouds",
                            "description": "scattered clouds",
                            "icon": "03n"
                        }
                    ],
                    "pop": 0.4
                },
                {
                    "dt": 1636135200,
                    "temp": 6.71,
                    "feels_like": 5.21,
                    "pressure": 1027,
                    "humidity": 92,
                    "dew_point": 5.66,
                    "uvi": 0,
                    "clouds": 37,
                    "visibility": 10000,
                    "wind_speed": 2.16,
                    "wind_deg": 290,
                    "wind_gust": 2.66,
                    "weather": [
                        {
                            "id": 802,
                            "main": "Clouds",
                            "description": "scattered clouds",
                            "icon": "03n"
                        }
                    ],
                    "pop": 0.2
                }
            ],
            "daily": [
                {
                    "dt": 1635937200,
                    "sunrise": 1635921211,
                    "sunset": 1635955733,
                    "moonrise": 1635912840,
                    "moonset": 1635954420,
                    "moon_phase": 0.94,
                    "temp": {
                        "day": 7.77,
                        "min": 4.51,
                        "max": 8.34,
                        "night": 5.64,
                        "eve": 6.48,
                        "morn": 4.83
                    },
                    "feels_like": {
                        "day": 6.34,
                        "night": 4.26,
                        "eve": 6.48,
                        "morn": 3.54
                    },
                    "pressure": 1001,
                    "humidity": 84,
                    "dew_point": 5.37,
                    "wind_speed": 2.42,
                    "wind_deg": 52,
                    "wind_gust": 4.06,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "clouds": 100,
                    "pop": 0.64,
                    "rain": 0.99,
                    "uvi": 0.67
                },
                {
                    "dt": 1636023600,
                    "sunrise": 1636007716,
                    "sunset": 1636042031,
                    "moonrise": 1636004460,
                    "moonset": 1636041960,
                    "moon_phase": 0,
                    "temp": {
                        "day": 6.25,
                        "min": 2.9,
                        "max": 8.72,
                        "night": 4.72,
                        "eve": 5.31,
                        "morn": 3.15
                    },
                    "feels_like": {
                        "day": 3.76,
                        "night": 2.87,
                        "eve": 3.05,
                        "morn": 0.69
                    },
                    "pressure": 1006,
                    "humidity": 95,
                    "dew_point": 5.69,
                    "wind_speed": 3.79,
                    "wind_deg": 201,
                    "wind_gust": 8.66,
                    "weather": [
                        {
                            "id": 501,
                            "main": "Rain",
                            "description": "moderate rain",
                            "icon": "10d"
                        }
                    ],
                    "clouds": 71,
                    "pop": 0.81,
                    "rain": 3.51,
                    "uvi": 0.7
                },
                {
                    "dt": 1636110000,
                    "sunrise": 1636094221,
                    "sunset": 1636128331,
                    "moonrise": 1636096260,
                    "moonset": 1636129800,
                    "moon_phase": 0.02,
                    "temp": {
                        "day": 10.4,
                        "min": 4.33,
                        "max": 11.55,
                        "night": 6.44,
                        "eve": 7.24,
                        "morn": 4.34
                    },
                    "feels_like": {
                        "day": 9.51,
                        "night": 4.67,
                        "eve": 5.85,
                        "morn": 2.56
                    },
                    "pressure": 1023,
                    "humidity": 77,
                    "dew_point": 6.74,
                    "wind_speed": 2.85,
                    "wind_deg": 321,
                    "wind_gust": 5.59,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "clouds": 9,
                    "pop": 0.48,
                    "rain": 0.39,
                    "uvi": 0.99
                },
                {
                    "dt": 1636196400,
                    "sunrise": 1636180725,
                    "sunset": 1636214632,
                    "moonrise": 1636188180,
                    "moonset": 1636218060,
                    "moon_phase": 0.06,
                    "temp": {
                        "day": 8.03,
                        "min": 3.65,
                        "max": 9.56,
                        "night": 8.72,
                        "eve": 8.9,
                        "morn": 3.65
                    },
                    "feels_like": {
                        "day": 5.69,
                        "night": 6.16,
                        "eve": 6.58,
                        "morn": 0.52
                    },
                    "pressure": 1028,
                    "humidity": 85,
                    "dew_point": 5.76,
                    "wind_speed": 4.6,
                    "wind_deg": 218,
                    "wind_gust": 10.77,
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04d"
                        }
                    ],
                    "clouds": 97,
                    "pop": 0,
                    "uvi": 0.65
                },
                {
                    "dt": 1636282800,
                    "sunrise": 1636267230,
                    "sunset": 1636300935,
                    "moonrise": 1636279860,
                    "moonset": 1636306980,
                    "moon_phase": 0.1,
                    "temp": {
                        "day": 11.32,
                        "min": 7.72,
                        "max": 11.32,
                        "night": 8.62,
                        "eve": 8.7,
                        "morn": 8.83
                    },
                    "feels_like": {
                        "day": 10.31,
                        "night": 5.81,
                        "eve": 5.77,
                        "morn": 5.63
                    },
                    "pressure": 1014,
                    "humidity": 69,
                    "dew_point": 5.97,
                    "wind_speed": 6.44,
                    "wind_deg": 266,
                    "wind_gust": 13.82,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "clouds": 94,
                    "pop": 0.39,
                    "rain": 0.8,
                    "uvi": 0.36
                },
                {
                    "dt": 1636369200,
                    "sunrise": 1636353735,
                    "sunset": 1636387240,
                    "moonrise": 1636370760,
                    "moonset": 1636396860,
                    "moon_phase": 0.14,
                    "temp": {
                        "day": 10.35,
                        "min": 5.06,
                        "max": 10.35,
                        "night": 5.06,
                        "eve": 6.14,
                        "morn": 8.33
                    },
                    "feels_like": {
                        "day": 9.45,
                        "night": 3.77,
                        "eve": 4.9,
                        "morn": 5.62
                    },
                    "pressure": 1020,
                    "humidity": 77,
                    "dew_point": 6.57,
                    "wind_speed": 4.72,
                    "wind_deg": 272,
                    "wind_gust": 10.59,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "clouds": 93,
                    "pop": 0.72,
                    "rain": 2.01,
                    "uvi": 0.66
                },
                {
                    "dt": 1636455600,
                    "sunrise": 1636440239,
                    "sunset": 1636473547,
                    "moonrise": 1636460700,
                    "moonset": 1636487520,
                    "moon_phase": 0.18,
                    "temp": {
                        "day": 7.99,
                        "min": 4.43,
                        "max": 9.76,
                        "night": 9.76,
                        "eve": 9.23,
                        "morn": 5.13
                    },
                    "feels_like": {
                        "day": 4.6,
                        "night": 7.17,
                        "eve": 6.32,
                        "morn": 2.3
                    },
                    "pressure": 1025,
                    "humidity": 80,
                    "dew_point": 4.89,
                    "wind_speed": 6.27,
                    "wind_deg": 210,
                    "wind_gust": 13.87,
                    "weather": [
                        {
                            "id": 804,
                            "main": "Clouds",
                            "description": "overcast clouds",
                            "icon": "04d"
                        }
                    ],
                    "clouds": 100,
                    "pop": 0.15,
                    "uvi": 1
                },
                {
                    "dt": 1636542000,
                    "sunrise": 1636526743,
                    "sunset": 1636559856,
                    "moonrise": 1636549620,
                    "moonset": 1636578660,
                    "moon_phase": 0.21,
                    "temp": {
                        "day": 13.4,
                        "min": 8.03,
                        "max": 13.4,
                        "night": 8.03,
                        "eve": 9.83,
                        "morn": 10.51
                    },
                    "feels_like": {
                        "day": 12.36,
                        "night": 5.03,
                        "eve": 6.77,
                        "morn": 9.52
                    },
                    "pressure": 1016,
                    "humidity": 60,
                    "dew_point": 5.8,
                    "wind_speed": 8.79,
                    "wind_deg": 224,
                    "wind_gust": 17.59,
                    "weather": [
                        {
                            "id": 500,
                            "main": "Rain",
                            "description": "light rain",
                            "icon": "10d"
                        }
                    ],
                    "clouds": 23,
                    "pop": 0.69,
                    "rain": 0.71,
                    "uvi": 1
                }
            ]
        }
