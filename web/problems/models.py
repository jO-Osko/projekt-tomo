import json
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from rest_framework.authtoken.models import Token
from simple_history.models import HistoricalRecords
from utils import is_json_string_list, truncate
from utils.models import OrderWithRespectToMixin
from taggit.managers import TaggableManager
from attempts.models import Attempt


class Problem(OrderWithRespectToMixin, models.Model):
    title = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    problem_set = models.ForeignKey('courses.ProblemSet', related_name='problems')
    history = HistoricalRecords()
    tags = TaggableManager(blank=True)

    class Meta:
        order_with_respect_to = 'problem_set'

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return '{}#{}'.format(self.problem_set.get_absolute_url(), self.anchor())

    def anchor(self):
        return 'problem-{}'.format(self.pk)

    def user_attempts(self, user):
        return user.attempts.filter(part__problem=self)

    def user_solutions(self, user):
        return {attempt.part.id: attempt.solution for attempt in self.user_attempts(user)}

    def attempt_file(self, user):
        authentication_token = Token.objects.get(user=user)
        solutions = self.user_solutions(user)
        parts = [(part, solutions.get(part.id, '')) for part in self.parts.all()]
        url = settings.SUBMISSION_URL + reverse('attempts-submit')
        filename = "{0}.py".format(slugify(self.title))
        contents = render_to_string("python/attempt.py", {
            "problem": self,
            "parts": parts,
            "submission_url": url,
            "authentication_token": authentication_token
        })
        return filename, contents

    def student_success(self):
        student_count = self.problem_set.course.students.count()
        attempts = Attempt.objects.filter(user__courses=self.problem_set.course,
                                          part__problem=self)
        submitted_count = attempts.count()
        valid_count = attempts.filter(valid=True).count()
        part_count = Part.objects.filter(problem=self).count()
        invalid_count = submitted_count - valid_count
        total_count = student_count * part_count

        if total_count:
            valid_percentage = int(100.0 * valid_count / total_count)
            invalid_percentage = int(100.0 * invalid_count / total_count)
        else:
            valid_percentage = 0
            invalid_percentage = 0

        empty_percentage = 100 - valid_percentage - invalid_percentage
        return {
            'valid': valid_percentage,
            'invalid': invalid_percentage,
            'empty': empty_percentage
        }

    def edit_file(self, user):
        authentication_token = Token.objects.get(user=user)
        url = settings.SUBMISSION_URL + reverse('problems-submit')
        filename = "{0}-edit.py".format(slugify(self.title))
        contents = render_to_string("python/edit.py", {
            "problem": self,
            "submission_url": url,
            "authentication_token": authentication_token
        })
        return filename, contents

    def valid(self, user):
        '''
        Check whether user has valid attempts for all parts of
        this problem.
        '''
        return self.valid_parts(user).count() == self.parts.count()

    def invalid(self, user):
        '''
        Check whether user has some invalid attempts for this problem.
        '''
        return self.attempted(user) and self.valid_parts(user).count() == 0

    def valid_parts(self, user):
        '''
        Return the QuerySet object of problem parts that have valid attempt by the given
        user.
        '''
        return self.parts.filter(attempts__user=user, attempts__valid=True)

    def attempted_parts(self, user):
        '''
        Return the queryset of all parts for which user has submitted attempts for.
        '''
        return user.attempts.filter(part__in=self.parts.all())

    def attempted(self, user):
        '''
        Return the queryset of all parts for which user has submitted attempts for.
        '''
        return self.attempted_parts(user).count() > 0

    def attempts_by_user(self):
        attempts = {}
        for part in self.parts.all():
            for attempt in part.attempts.all():
                if attempt.user in attempts:
                    attempts[attempt.user][part] = attempt
                else:
                    attempts[attempt.user] = {part: attempt}
        sorted_attempts = []
        for user in sorted(attempts.keys()):
            user_attempts = [attempts[user].get(part) for part in self.parts.all()]
            sorted_attempts.append((user, user_attempts))
        return sorted_attempts

    def progress_bar_width(self):
        parts_count = self.parts.count()
        if parts_count:
            return "{0}%".format(100.0 / parts_count)
        else:
            return "0%"


class Part(OrderWithRespectToMixin, models.Model):
    problem = models.ForeignKey(Problem, related_name='parts')
    description = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    validation = models.TextField(blank=True)
    secret = models.TextField(default="[]", validators=[is_json_string_list])
    history = HistoricalRecords()

    class Meta:
        order_with_respect_to = 'problem'

    def __unicode__(self):
        return u'@{0:06d} ({1})'.format(self.pk, truncate(self.description))

    def get_absolute_url(self):
        return '{}#{}'.format(self.problem_set.get_absolute_url(), self.anchor())

    def anchor(self):
        return 'part-{}'.format(self.pk)


    def check_secret(self, secret):
        '''
        Checks whether a submitted secret corresponds to the official one.

        The function accepts a secret (list of strings) and returns the pair:
        True, None -- if secret matches the official one
        False, None -- if secret has an incorrect length
        False, i -- if secret first differs from the official one at index i
        '''
        official_secret = json.loads(self.secret)
        if len(official_secret) != len(secret):
            return False, None
        for i in range(len(secret)):
            if secret[i] != official_secret[i]:
                return False, i
        return True, None

    def valid(self, user):
        '''
        Check whether user has submitted attempt for this part
        that is marked as valid.
        '''
        return user.attempts.filter(part=self, valid=True).count() == 1

    def attempted(self, user):
        '''
        Check whether user has submitted attempt for this part.
        '''
        return user.attempts.filter(part=self).count() >= 1

    def student_success(self):
        student_count = self.problem.problem_set.course.students.count()
        attempts = self.attempts.filter(user__courses=self.problem.problem_set.course)
        submitted_count = attempts.count()
        valid_count = attempts.filter(valid=True).count()
        invalid_count = submitted_count - valid_count
        total_count = student_count

        if total_count:
            valid_percentage = int(100.0 * valid_count / total_count)
            invalid_percentage = int(100.0 * invalid_count / total_count)
        else:
            valid_percentage = 0
            invalid_percentage = 0

        empty_percentage = 100 - valid_percentage - invalid_percentage
        return {
            'valid': valid_percentage,
            'invalid': invalid_percentage,
            'empty': empty_percentage
        }
