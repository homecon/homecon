#!/usr/bin/env python3
######################################################################################
#    Copyright 2016 Brecht Baeten
#    This file is part of HomeCon.
#
#    HomeCon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    HomeCon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with HomeCon.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

import logging
import jwt
import datetime


logger = logging.getLogger('')


class Authentication(object):
    def __init__(self,db,secret,algorithm='HS256',token_exp=30*24*3600):
        """
        Parameters:
            db:             the database instance
            secret:         string
            algorithm:      string
        """

        self._db = db
        self._secret = secret
        self._algorithm = algorithm

        self._token_exp = token_exp

    def request_token(self,username,password):
        user = self._db.verify_user(username,password)
        
        if user:
            # return the token
            iat = datetime.datetime.utcnow()
            exp = iat + datetime.timedelta(seconds=self._token_exp)

            payload = {'id': user[0], 'username':user[1], 'permission':user[2], 'exp':exp, 'iat':iat}

            return self._encode(payload)
        else:
            return False

    def renew_token(self,token):

        payload = self._decode(token)
        
        if payload:
            # return a new token
            iat = datetime.datetime.utcnow()
            exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=self._token_exp)

            payload['exp'] = exp

            return self._encode(payload)
        else:
            return False

    def check_token(self,token):
        return self._decode(self,token)

    def _encode(self,payload):
        """
        Parameters:
            payload:        dict
        """
        return jwt.encode(payload, self._secret, self._algorithm).decode("utf-8")

    def _decode(self,token):
        """
        Parameters:
            token:          string
        """
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except:
            return False


