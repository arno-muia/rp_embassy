"""URL routing for the public content API."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'sermons', views.SermonViewSet, basename='sermon')
router.register(r'series', views.SeriesViewSet, basename='series')
router.register(r'leaders', views.LeaderViewSet, basename='leader')
router.register(r'testimonials', views.TestimonialViewSet, basename='testimonial')
router.register(r'academy', views.AcademyModuleViewSet, basename='academy')

urlpatterns = router.urls + [
    path('site-config', views.site_config, name='site-config'),
    path('contact', views.contact_submit, name='contact-submit'),
    path('rsvp', views.rsvp_submit, name='rsvp-submit'),
]
