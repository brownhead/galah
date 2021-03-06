from galah.web import app
from galah.web.auth import account_type_required
from galah.db.models import Assignment, Submission, Archive
from galah.base.filemagic import zipdir
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import send_file, abort
from flask.ext.login import current_user
from galah.web.util import GalahWebAdapter
import os.path
import subprocess
import tempfile
import datetime
import logging
import sys

logger = \
    GalahWebAdapter(logging.getLogger("galah.web.views.download_submission"))

@app.route("/assignments/<assignment_id>/<submission_id>/download.zip")
@account_type_required(("student", "teacher", "teaching_assistant"))
def download_submission(assignment_id, submission_id):
    # Figure out which assignment the user asked for.
    try:
        assignment_id = ObjectId(assignment_id)
        assignment = Assignment.objects.get(id = assignment_id)
    except (InvalidId, Assignment.DoesNotExist) as e:
        logger.info("Could not retrieve assignment: %s.", str(e))

        abort(404)

    # Figure out which submission the user is trying to download
    try:
        submission_id = ObjectId(submission_id)
        submission = Submission.objects.get(id = submission_id)
    except InvalidId, Submission.DoesNotExist:
        logger.info("Could not retrieve submission: %s.", str(e))

        abort(404)

    if current_user.account_type == "student" and \
            submission.user != current_user.id:
        logger.info("User tried to download submission they can't access.")

        abort(404)

    # Find any expired archives and remove them
    deleted_files = []
    for i in Archive.objects(expires__lt = datetime.datetime.today()).limit(5):
        if i.file_location:
            deleted_files.append(i.file_location)

            try:
                os.remove(i.file_location)
            except OSError as e:
                logger.warning(
                    "Could not remove expired archive at %s: %s.",
                    i.file_location, str(e)
                )

        i.delete()

    if deleted_files:
        logger.info("Deleted archives %s.", str(deleted_files))

    new_archive = Archive(
        requester = current_user.id,
        archive_type = "single_submission"
    )

    new_archive.expires = \
        datetime.datetime.today() + app.config["STUDENT_ARCHIVE_LIFETIME"]

    archive_file_name = ""
    try:
        # Create the actual archive file.
        # TODO: Create it in galah's /var/ directory
        archive_fd, archive_file_name = tempfile.mkstemp(suffix = ".zip")

        # Close the file because we won't actually do any writing to it,
        # rather tar will.
        os.close(archive_fd)

        # Run zip and do the actual archiving. Will block until it's finished.
        zipdir(submission.getFilePath(), archive_file_name)

        new_archive.file_location = archive_file_name

        new_archive.save(force_insert = True)

        return send_file(archive_file_name)
    except Exception as e:
        logger.exception("An error occured while creating an archive.")

        # If we created a temporary archive file we need to delete it.
        new_archive.file_location = None
        if archive_file_name:
            os.remove(archive_file_name)

        new_archive.error_string = str(e)
        new_archive.save(force_insert = True)

        abort(500)
