from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from connectus.app_helper.helper import Util
from connectus.courses.models import CourseRegistration
from connectus.messaging.models import Announcement, Messaging, MessageForm
from connectus.user_info.models import ParentStudentRelation

@login_required
def inbox(req):
  limit = 10
  messages = Messaging.objects.filter(to__id=req.user.id).\
                               order_by('-created_at')[:limit]
  return render_to_response('messaging/inbox.html', {
                              'messages': messages,
                            },
                            context_instance=RequestContext(req))

@login_required
def view_message(req, msg_id):
  msg = Messaging.objects.get(id=msg_id, to=req.user.id)
  if msg:
    msg.read = True
    msg.save()
    return render_to_response('messaging/view_message.html', {
                                'msg': msg,
                              },
                              context_instance=RequestContext(req))
  else:
    return HttpResponseRedirect('/messages/')

@login_required
def new(req):
  if req.method == 'POST':
    form = MessageForm(req.POST)
    # TODO: Validate form better here
    if form.is_valid():
      msg = form.save(commit=False)
      msg.sender = req.user
      msg.save()
      return HttpResponseRedirect('/messages/')
  else:
    form = MessageForm()

  return render_to_response('messaging/new.html',
                            { 'form': form  },
                            context_instance=RequestContext(req))

@login_required
def delete(req, msg_id):
  msg = get_object_or_404(Messaging, pk=msg_id)
  msg.delete()
  coming_from = req.META['HTTP_REFERER']
  return HttpResponseRedirect(coming_from)

@login_required
def make_unread(req, msg_id):
  msg = get_object_or_404(Messaging, pk=msg_id)
  msg.read = False
  msg.save()
  return HttpResponseRedirect('/messages')

@login_required
def view_announcements(req):
  student = req.user
  if Util.is_in_group(req.user, 'Parent'):
    relations = ParentStudentRelation.objects.filter(parent=req.user)
    if relations:
      #TODO: should be querying for all children
      student = relations[0].student
  registrations = CourseRegistration.objects.filter(student=student)
  course_ids = []
  for reg in registrations:
    course_ids.append(reg.course.id)
  announcements = Announcement.objects.filter(course__id__in=course_ids).\
                                       order_by('-created_at') 

  return render_to_response('messaging/view_announcements.html', {
                              'announcements': announcements,
                            },
                            context_instance=RequestContext(req))
