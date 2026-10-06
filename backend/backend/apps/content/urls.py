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
    path('homepage', views.homepage, name='homepage'),
    path('about', views.about_page, name='about-page'),
    path('visit', views.visit_page, name='visit-page'),
    path('sermons-page', views.sermons_page, name='sermons-page'),
    path('give', views.give_page, name='give-page'),
    path('contact-page', views.contact_page, name='contact-page'),
    path('site-config', views.site_config, name='site-config'),
    path('sections', views.sections, name='sections'),
    path('contact', views.contact_submit, name='contact-submit'),
    path('rsvp', views.rsvp_submit, name='rsvp-submit'),
]
