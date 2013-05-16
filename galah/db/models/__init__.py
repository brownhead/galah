# Copyright 2012-2013 John Sullivan
# Copyright 2012-2013 Other contributors as noted in the CONTRIBUTORS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

import mongoengine

# If were importing models from another component of galah the users shouldn't
# (and can't) be loaded.
try:
    import users
    from users import User

    import invitations
    from invitations import Invitation
except ImportError:
    pass

import classes
from classes import Class

import assignments
from assignments import Assignment, TestHarness

import submissions
from submissions import Submission, TestResult

import archives
from archives import Archive

import csv
from csv import CSV
