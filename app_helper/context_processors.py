from django.core.urlresolvers import reverse, resolve
from connectus.app_helper.helper import NavigationTree, Util, ViewMenuMapping
from connectus.courses.models import Course, CourseRegistration

def sidebar(request):
  # TODO: order by course title
  if request.user.is_anonymous():
    return {}

  user_groups = request.user.groups.all()
  if user_groups:
    menus = NavigationTree.get_main_navi(user_groups)
  else:
    return {} 
  
  #TODO need a better way to check for groups
  if user_groups[0].name == 'Teacher': 
    #TODO: check which class this teacher belongs to 
    courses = Course.objects.all()
  elif user_groups[0].name == 'Student':
    regs = CourseRegistration.objects.filter(student=request.user)
    course_ids = []
    for reg in regs:
      course_ids.append(reg.course.id)
    courses = Course.objects.filter(id__in=course_ids)
  else:
    courses = []

  return {
    'courses': courses,
    'menus': menus
  }

def navigation_view_solver(request):
  selected_css_class = 'selected'
  view_func, args, kwargs = resolve(request.path)
  view_name = Util.construct_module_name(view_func)
  selected_id = ViewMenuMapping.mapping.get(view_name)
  return {
    'selected_id': selected_id
  }
