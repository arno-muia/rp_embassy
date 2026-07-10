# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Announcement(models.Model):
    id = models.TextField(primary_key=True)
    title = models.TextField()
    content = models.TextField()
    priority = models.TextField()  # This field type is a guess.
    displayfrom = models.DateTimeField(db_column='displayFrom')  # Field name made lowercase.
    displayuntil = models.DateTimeField(db_column='displayUntil', blank=True, null=True)  # Field name made lowercase.
    targetaudience = models.TextField(db_column='targetAudience')  # Field name made lowercase. This field type is a guess.
    imageurl = models.TextField(db_column='imageUrl', blank=True, null=True)  # Field name made lowercase.
    linkurl = models.TextField(db_column='linkUrl', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive')  # Field name made lowercase.
    createdbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='createdById', blank=True, null=True)  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Announcement'


class Attendance(models.Model):
    id = models.TextField(primary_key=True)
    memberid = models.ForeignKey('Member', models.DO_NOTHING, db_column='memberId', blank=True, null=True)  # Field name made lowercase.
    visitorid = models.ForeignKey('Visitor', models.DO_NOTHING, db_column='visitorId', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.ForeignKey('Servicesession', models.DO_NOTHING, db_column='sessionId')  # Field name made lowercase.
    method = models.TextField()  # This field type is a guess.
    checkedinbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='checkedInById', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    offlinesynced = models.BooleanField(db_column='offlineSynced')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Attendance'
        unique_together = (('memberid', 'sessionid'), ('visitorid', 'sessionid'),)


class Auditlog(models.Model):
    id = models.TextField(primary_key=True)
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userId', blank=True, null=True)  # Field name made lowercase.
    action = models.TextField()  # This field type is a guess.
    entitytype = models.TextField(db_column='entityType')  # Field name made lowercase.
    entityid = models.TextField(db_column='entityId', blank=True, null=True)  # Field name made lowercase.
    details = models.JSONField(blank=True, null=True)
    ipaddress = models.TextField(db_column='ipAddress', blank=True, null=True)  # Field name made lowercase.
    useragent = models.TextField(db_column='userAgent', blank=True, null=True)  # Field name made lowercase.
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'AuditLog'


class Carecase(models.Model):
    id = models.TextField(primary_key=True)
    householdid = models.ForeignKey('Household', models.DO_NOTHING, db_column='householdId', blank=True, null=True)  # Field name made lowercase.
    memberid = models.ForeignKey('Member', models.DO_NOTHING, db_column='memberId', blank=True, null=True)  # Field name made lowercase.
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    type = models.TextField()  # This field type is a guess.
    priority = models.TextField()  # This field type is a guess.
    status = models.TextField()  # This field type is a guess.
    assignedtoid = models.ForeignKey('User', models.DO_NOTHING, db_column='assignedToId', blank=True, null=True)  # Field name made lowercase.
    openeddate = models.DateTimeField(db_column='openedDate')  # Field name made lowercase.
    resolveddate = models.DateTimeField(db_column='resolvedDate', blank=True, null=True)  # Field name made lowercase.
    confidential = models.BooleanField()
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    createdbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='createdById', related_name='carecase_createdbyid_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CareCase'


class Carenote(models.Model):
    id = models.TextField(primary_key=True)
    carecaseid = models.ForeignKey(Carecase, models.DO_NOTHING, db_column='careCaseId')  # Field name made lowercase.
    note = models.TextField()
    authorid = models.ForeignKey('User', models.DO_NOTHING, db_column='authorId')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CareNote'


class Cellgroup(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    meetingday = models.TextField(db_column='meetingDay', blank=True, null=True)  # Field name made lowercase.
    meetingtime = models.TextField(db_column='meetingTime', blank=True, null=True)  # Field name made lowercase.
    location = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    leaderid = models.ForeignKey('Member', models.DO_NOTHING, db_column='leaderId')  # Field name made lowercase.
    coleaderid = models.ForeignKey('Member', models.DO_NOTHING, db_column='coLeaderId', related_name='cellgroup_coleaderid_set', blank=True, null=True)  # Field name made lowercase.
    maxcapacity = models.IntegerField(db_column='maxCapacity', blank=True, null=True)  # Field name made lowercase.
    status = models.TextField()  # This field type is a guess.
    campusid = models.TextField(db_column='campusId', blank=True, null=True)  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CellGroup'


class Cellgroupmembership(models.Model):
    id = models.TextField(primary_key=True)
    cellgroupid = models.ForeignKey(Cellgroup, models.DO_NOTHING, db_column='cellGroupId')  # Field name made lowercase.
    memberid = models.OneToOneField('Member', models.DO_NOTHING, db_column='memberId')  # Field name made lowercase.
    joindate = models.DateTimeField(db_column='joinDate')  # Field name made lowercase.
    role = models.TextField()  # This field type is a guess.
    status = models.TextField()  # This field type is a guess.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CellGroupMembership'


class Churchevent(models.Model):
    id = models.TextField(primary_key=True)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    type = models.TextField()  # This field type is a guess.
    startdatetime = models.DateTimeField(db_column='startDateTime')  # Field name made lowercase.
    enddatetime = models.DateTimeField(db_column='endDateTime', blank=True, null=True)  # Field name made lowercase.
    location = models.TextField(blank=True, null=True)
    imageurl = models.TextField(db_column='imageUrl', blank=True, null=True)  # Field name made lowercase.
    galleryurl = models.TextField(db_column='galleryUrl', blank=True, null=True)  # Field name made lowercase.
    registrationrequired = models.BooleanField(db_column='registrationRequired')  # Field name made lowercase.
    maxattendees = models.IntegerField(db_column='maxAttendees', blank=True, null=True)  # Field name made lowercase.
    costcents = models.IntegerField(db_column='costCents', blank=True, null=True)  # Field name made lowercase.
    registrationopendate = models.DateTimeField(db_column='registrationOpenDate', blank=True, null=True)  # Field name made lowercase.
    status = models.TextField()  # This field type is a guess.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    createdbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='createdById', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ChurchEvent'


class Contactsubmission(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    email = models.TextField()
    phone = models.TextField(blank=True, null=True)
    message = models.TextField()
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ContactSubmission'


class Discipleshiplesson(models.Model):
    id = models.TextField(primary_key=True)
    moduleid = models.ForeignKey('Discipleshipmodule', models.DO_NOTHING, db_column='moduleId')  # Field name made lowercase.
    title = models.TextField()
    content = models.TextField(blank=True, null=True)
    videourl = models.TextField(db_column='videoUrl', blank=True, null=True)  # Field name made lowercase.
    audiourl = models.TextField(db_column='audioUrl', blank=True, null=True)  # Field name made lowercase.
    downloadableresources = models.JSONField(db_column='downloadableResources', blank=True, null=True)  # Field name made lowercase.
    sortorder = models.IntegerField(db_column='sortOrder')  # Field name made lowercase.
    durationminutes = models.IntegerField(db_column='durationMinutes', blank=True, null=True)  # Field name made lowercase.
    ispublished = models.BooleanField(db_column='isPublished')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DiscipleshipLesson'


class Discipleshipmodule(models.Model):
    id = models.TextField(primary_key=True)
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    instructorid = models.ForeignKey('Member', models.DO_NOTHING, db_column='instructorId', blank=True, null=True)  # Field name made lowercase.
    sortorder = models.IntegerField(db_column='sortOrder')  # Field name made lowercase.
    prerequisitemoduleid = models.ForeignKey('self', models.DO_NOTHING, db_column='prerequisiteModuleId', blank=True, null=True)  # Field name made lowercase.
    estimatedhours = models.IntegerField(db_column='estimatedHours', blank=True, null=True)  # Field name made lowercase.
    certificatetemplate = models.TextField(db_column='certificateTemplate', blank=True, null=True)  # Field name made lowercase.
    ispublished = models.BooleanField(db_column='isPublished')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DiscipleshipModule'


class Eventregistration(models.Model):
    id = models.TextField(primary_key=True)
    memberid = models.ForeignKey('Member', models.DO_NOTHING, db_column='memberId', blank=True, null=True)  # Field name made lowercase.
    eventid = models.ForeignKey(Churchevent, models.DO_NOTHING, db_column='eventId')  # Field name made lowercase.
    walkinname = models.TextField(db_column='walkInName', blank=True, null=True)  # Field name made lowercase.
    walkinphone = models.TextField(db_column='walkInPhone', blank=True, null=True)  # Field name made lowercase.
    walkinemail = models.TextField(db_column='walkInEmail', blank=True, null=True)  # Field name made lowercase.
    registrationdate = models.DateTimeField(db_column='registrationDate')  # Field name made lowercase.
    attended = models.BooleanField(blank=True, null=True)
    paymentstatus = models.TextField(db_column='paymentStatus', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    notes = models.TextField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'EventRegistration'


class Followup(models.Model):
    id = models.TextField(primary_key=True)
    visitorid = models.ForeignKey('Visitor', models.DO_NOTHING, db_column='visitorId')  # Field name made lowercase.
    type = models.TextField()  # This field type is a guess.
    assignedtoid = models.ForeignKey('User', models.DO_NOTHING, db_column='assignedToId')  # Field name made lowercase.
    duedate = models.DateTimeField(db_column='dueDate')  # Field name made lowercase.
    completeddate = models.DateTimeField(db_column='completedDate', blank=True, null=True)  # Field name made lowercase.
    status = models.TextField()  # This field type is a guess.
    notes = models.TextField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FollowUp'


class Givingcampaign(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    fund = models.TextField()  # This field type is a guess.
    targetamountcents = models.IntegerField(db_column='targetAmountCents', blank=True, null=True)  # Field name made lowercase.
    currentamountcents = models.IntegerField(db_column='currentAmountCents')  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='startDate')  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='endDate', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GivingCampaign'


class Givingtransaction(models.Model):
    id = models.TextField(primary_key=True)
    memberid = models.ForeignKey('Member', models.DO_NOTHING, db_column='memberId', blank=True, null=True)  # Field name made lowercase.
    householdid = models.ForeignKey('Household', models.DO_NOTHING, db_column='householdId', blank=True, null=True)  # Field name made lowercase.
    amountcents = models.IntegerField(db_column='amountCents')  # Field name made lowercase.
    currency = models.TextField()
    method = models.TextField()  # This field type is a guess.
    fund = models.TextField()  # This field type is a guess.
    reference = models.TextField(blank=True, null=True)
    status = models.TextField()  # This field type is a guess.
    mpesarequestid = models.TextField(db_column='mpesaRequestId', blank=True, null=True)  # Field name made lowercase.
    mpesacallbackdata = models.JSONField(db_column='mpesaCallbackData', blank=True, null=True)  # Field name made lowercase.
    failurereason = models.TextField(db_column='failureReason', blank=True, null=True)  # Field name made lowercase.
    isrecurring = models.BooleanField(db_column='isRecurring')  # Field name made lowercase.
    recurringfrequency = models.TextField(db_column='recurringFrequency', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    recurringenddate = models.DateTimeField(db_column='recurringEndDate', blank=True, null=True)  # Field name made lowercase.
    completedat = models.DateTimeField(db_column='completedAt', blank=True, null=True)  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    createdbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='createdById', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GivingTransaction'


class Household(models.Model):
    id = models.TextField(primary_key=True)
    householdname = models.TextField(db_column='householdName', blank=True, null=True)  # Field name made lowercase.
    address = models.JSONField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    anniversarydate = models.DateTimeField(db_column='anniversaryDate', blank=True, null=True)  # Field name made lowercase.
    status = models.TextField()  # This field type is a guess.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.
    createdbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='createdById', blank=True, null=True)  # Field name made lowercase.
    updatedbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='updatedById', related_name='household_updatedbyid_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Household'


class Householdmember(models.Model):
    pk = models.CompositePrimaryKey('householdId', 'memberId')
    householdid = models.ForeignKey(Household, models.DO_NOTHING, db_column='householdId')  # Field name made lowercase.
    memberid = models.OneToOneField('Member', models.DO_NOTHING, db_column='memberId')  # Field name made lowercase.
    role = models.TextField()  # This field type is a guess.
    canpickup = models.BooleanField(db_column='canPickUp')  # Field name made lowercase.
    isprimarycontact = models.BooleanField(db_column='isPrimaryContact')  # Field name made lowercase.
    joinedat = models.DateTimeField(db_column='joinedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'HouseholdMember'


class Member(models.Model):
    id = models.TextField(primary_key=True)
    firstname = models.TextField(db_column='firstName')  # Field name made lowercase.
    lastname = models.TextField(db_column='lastName')  # Field name made lowercase.
    email = models.TextField(unique=True, blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)  # This field type is a guess.
    dateofbirth = models.DateTimeField(db_column='dateOfBirth', blank=True, null=True)  # Field name made lowercase.
    maritalstatus = models.TextField(db_column='maritalStatus', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    membershipdate = models.DateTimeField(db_column='membershipDate', blank=True, null=True)  # Field name made lowercase.
    baptismdate = models.DateTimeField(db_column='baptismDate', blank=True, null=True)  # Field name made lowercase.
    discipleshiplevel = models.TextField(db_column='discipleshipLevel')  # Field name made lowercase. This field type is a guess.
    spiritualgifts = models.TextField(db_column='spiritualGifts', blank=True, null=True)  # Field name made lowercase.
    ministryteams = models.TextField(db_column='ministryTeams', blank=True, null=True)  # Field name made lowercase.
    visitor = models.BooleanField()
    status = models.TextField()  # This field type is a guess.
    cellgroupid = models.ForeignKey(Cellgroup, models.DO_NOTHING, db_column='cellGroupId', blank=True, null=True)  # Field name made lowercase.
    householdid = models.ForeignKey(Household, models.DO_NOTHING, db_column='householdId', blank=True, null=True)  # Field name made lowercase.
    userid = models.OneToOneField('User', models.DO_NOTHING, db_column='userId', blank=True, null=True)  # Field name made lowercase.
    consentgiven = models.BooleanField(db_column='consentGiven')  # Field name made lowercase.
    consentdate = models.DateTimeField(db_column='consentDate', blank=True, null=True)  # Field name made lowercase.
    consentversion = models.TextField(db_column='consentVersion', blank=True, null=True)  # Field name made lowercase.
    profileimageurl = models.TextField(db_column='profileImageUrl', blank=True, null=True)  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    deletedat = models.DateTimeField(db_column='deletedAt', blank=True, null=True)  # Field name made lowercase.
    createdbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='createdById', related_name='member_createdbyid_set', blank=True, null=True)  # Field name made lowercase.
    updatedbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='updatedById', related_name='member_updatedbyid_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Member'


class Memberprogress(models.Model):
    id = models.TextField(primary_key=True)
    memberid = models.ForeignKey(Member, models.DO_NOTHING, db_column='memberId')  # Field name made lowercase.
    lessonid = models.ForeignKey(Discipleshiplesson, models.DO_NOTHING, db_column='lessonId')  # Field name made lowercase.
    status = models.TextField()  # This field type is a guess.
    startedat = models.DateTimeField(db_column='startedAt', blank=True, null=True)  # Field name made lowercase.
    completedat = models.DateTimeField(db_column='completedAt', blank=True, null=True)  # Field name made lowercase.
    quizscore = models.IntegerField(db_column='quizScore', blank=True, null=True)  # Field name made lowercase.
    quizattempts = models.IntegerField(db_column='quizAttempts')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MemberProgress'
        unique_together = (('memberid', 'lessonid'),)


class Messagelog(models.Model):
    id = models.TextField(primary_key=True)
    recipientid = models.ForeignKey(Member, models.DO_NOTHING, db_column='recipientId', blank=True, null=True)  # Field name made lowercase.
    type = models.TextField()  # This field type is a guess.
    subject = models.TextField(blank=True, null=True)
    body = models.TextField()
    status = models.TextField()  # This field type is a guess.
    sentat = models.DateTimeField(db_column='sentAt', blank=True, null=True)  # Field name made lowercase.
    deliveredat = models.DateTimeField(db_column='deliveredAt', blank=True, null=True)  # Field name made lowercase.
    failedat = models.DateTimeField(db_column='failedAt', blank=True, null=True)  # Field name made lowercase.
    failurereason = models.TextField(db_column='failureReason', blank=True, null=True)  # Field name made lowercase.
    externalid = models.TextField(db_column='externalId', blank=True, null=True)  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    createdbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='createdById', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MessageLog'


class Prayerrequest(models.Model):
    id = models.TextField(primary_key=True)
    requesterid = models.ForeignKey(Member, models.DO_NOTHING, db_column='requesterId', blank=True, null=True)  # Field name made lowercase.
    title = models.TextField()
    content = models.TextField()
    category = models.TextField(blank=True, null=True)  # This field type is a guess.
    isanonymous = models.BooleanField(db_column='isAnonymous')  # Field name made lowercase.
    ispublic = models.BooleanField(db_column='isPublic')  # Field name made lowercase.
    status = models.TextField()  # This field type is a guess.
    prayercount = models.IntegerField(db_column='prayerCount')  # Field name made lowercase.
    answereddate = models.DateTimeField(db_column='answeredDate', blank=True, null=True)  # Field name made lowercase.
    answerednote = models.TextField(db_column='answeredNote', blank=True, null=True)  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PrayerRequest'


class Prayersubmission(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    request = models.TextField()
    anonymous = models.BooleanField()
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PrayerSubmission'


class Publicsermon(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(unique=True)
    title = models.TextField()
    description = models.TextField()
    seriesid = models.ForeignKey('Sermonseries', models.DO_NOTHING, db_column='seriesId', blank=True, null=True)  # Field name made lowercase.
    seriesslug = models.TextField(db_column='seriesSlug')  # Field name made lowercase.
    seriestitle = models.TextField(db_column='seriesTitle')  # Field name made lowercase.
    scripture = models.TextField(blank=True, null=True)
    speaker = models.TextField()
    date = models.DateTimeField()
    videourl = models.TextField(db_column='videoUrl')  # Field name made lowercase.
    audiourl = models.TextField(db_column='audioUrl', blank=True, null=True)  # Field name made lowercase.
    notesurl = models.TextField(db_column='notesUrl', blank=True, null=True)  # Field name made lowercase.
    thumbnailurl = models.TextField(db_column='thumbnailUrl')  # Field name made lowercase.
    duration = models.TextField(blank=True, null=True)
    tags = models.JSONField()
    ispublished = models.BooleanField(db_column='isPublished')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PublicSermon'


class Quiz(models.Model):
    id = models.TextField(primary_key=True)
    lessonid = models.OneToOneField(Discipleshiplesson, models.DO_NOTHING, db_column='lessonId')  # Field name made lowercase.
    instructorid = models.ForeignKey(Member, models.DO_NOTHING, db_column='instructorId', blank=True, null=True)  # Field name made lowercase.
    title = models.TextField()
    passingscore = models.IntegerField(db_column='passingScore')  # Field name made lowercase.
    maxattempts = models.IntegerField(db_column='maxAttempts', blank=True, null=True)  # Field name made lowercase.
    shufflequestions = models.BooleanField(db_column='shuffleQuestions')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Quiz'


class Quizquestion(models.Model):
    id = models.TextField(primary_key=True)
    quizid = models.ForeignKey(Quiz, models.DO_NOTHING, db_column='quizId')  # Field name made lowercase.
    type = models.TextField()  # This field type is a guess.
    questiontext = models.TextField(db_column='questionText')  # Field name made lowercase.
    options = models.JSONField(blank=True, null=True)
    correctanswer = models.JSONField(db_column='correctAnswer')  # Field name made lowercase.
    explanation = models.TextField(blank=True, null=True)
    points = models.IntegerField()
    sortorder = models.IntegerField(db_column='sortOrder')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'QuizQuestion'


class Sermonseries(models.Model):
    id = models.TextField(primary_key=True)
    slug = models.TextField(unique=True)
    title = models.TextField()
    description = models.TextField()
    imageurl = models.TextField(db_column='imageUrl')  # Field name made lowercase.
    sermoncount = models.IntegerField(db_column='sermonCount')  # Field name made lowercase.
    sortorder = models.IntegerField(db_column='sortOrder')  # Field name made lowercase.
    ispublished = models.BooleanField(db_column='isPublished')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SermonSeries'


class Servicesession(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    type = models.TextField()  # This field type is a guess.
    starttime = models.DateTimeField(db_column='startTime')  # Field name made lowercase.
    endtime = models.DateTimeField(db_column='endTime', blank=True, null=True)  # Field name made lowercase.
    location = models.TextField(blank=True, null=True)
    qrtoken = models.TextField(db_column='qrToken', unique=True, blank=True, null=True)  # Field name made lowercase.
    status = models.TextField()  # This field type is a guess.
    campusid = models.TextField(db_column='campusId', blank=True, null=True)  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    createdbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='createdById', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ServiceSession'


class Systemconfig(models.Model):
    id = models.TextField(primary_key=True)
    key = models.TextField(unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True, null=True)
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    updatedbyid = models.ForeignKey('User', models.DO_NOTHING, db_column='updatedById', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SystemConfig'


class User(models.Model):
    id = models.TextField(primary_key=True)
    email = models.TextField(unique=True)
    passwordhash = models.TextField(db_column='passwordHash')  # Field name made lowercase.
    name = models.TextField()
    role = models.TextField()  # This field type is a guess.
    isactive = models.BooleanField(db_column='isActive')  # Field name made lowercase.
    mustchangepassword = models.BooleanField(db_column='mustChangePassword')  # Field name made lowercase.
    failedloginattempts = models.IntegerField(db_column='failedLoginAttempts')  # Field name made lowercase.
    lockeduntil = models.DateTimeField(db_column='lockedUntil', blank=True, null=True)  # Field name made lowercase.
    lastlogin = models.DateTimeField(db_column='lastLogin', blank=True, null=True)  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User'


class Visitrsvp(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    phone = models.TextField()
    email = models.TextField(blank=True, null=True)
    partysize = models.IntegerField(db_column='partySize')  # Field name made lowercase.
    firstvisit = models.BooleanField(db_column='firstVisit')  # Field name made lowercase.
    visitdate = models.DateTimeField(db_column='visitDate', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    status = models.TextField()
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'VisitRsvp'


class Visitor(models.Model):
    id = models.TextField(primary_key=True)
    firstname = models.TextField(db_column='firstName')  # Field name made lowercase.
    lastname = models.TextField(db_column='lastName')  # Field name made lowercase.
    email = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)  # This field type is a guess.
    dateofbirth = models.DateTimeField(db_column='dateOfBirth', blank=True, null=True)  # Field name made lowercase.
    source = models.TextField()  # This field type is a guess.
    heardaboutdetail = models.TextField(db_column='heardAboutDetail', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.ForeignKey(Servicesession, models.DO_NOTHING, db_column='sessionId')  # Field name made lowercase.
    followupstatus = models.TextField(db_column='followUpStatus')  # Field name made lowercase. This field type is a guess.
    assignedtoid = models.ForeignKey(User, models.DO_NOTHING, db_column='assignedToId', blank=True, null=True)  # Field name made lowercase.
    convertedtomemberid = models.OneToOneField(Member, models.DO_NOTHING, db_column='convertedToMemberId', blank=True, null=True)  # Field name made lowercase.
    consentgiven = models.BooleanField(db_column='consentGiven')  # Field name made lowercase.
    consentdate = models.DateTimeField(db_column='consentDate', blank=True, null=True)  # Field name made lowercase.
    visitcount = models.IntegerField(db_column='visitCount')  # Field name made lowercase.
    lastvisitdate = models.DateTimeField(db_column='lastVisitDate', blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.
    createdbyid = models.ForeignKey(User, models.DO_NOTHING, db_column='createdById', related_name='visitor_createdbyid_set', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Visitor'


class Volunteerassignment(models.Model):
    id = models.TextField(primary_key=True)
    memberid = models.ForeignKey(Member, models.DO_NOTHING, db_column='memberId')  # Field name made lowercase.
    roleid = models.ForeignKey('Volunteerrole', models.DO_NOTHING, db_column='roleId')  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='startDate')  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='endDate', blank=True, null=True)  # Field name made lowercase.
    status = models.TextField()  # This field type is a guess.
    notes = models.TextField(blank=True, null=True)
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'VolunteerAssignment'


class Volunteerrole(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    department = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    isactive = models.BooleanField(db_column='isActive')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'VolunteerRole'


class Websiteacademymodule(models.Model):
    id = models.TextField(primary_key=True)
    title = models.TextField()
    description = models.TextField()
    instructor = models.TextField()
    lessonscount = models.IntegerField(db_column='lessonsCount')  # Field name made lowercase.
    duration = models.TextField()
    sortorder = models.IntegerField(db_column='sortOrder')  # Field name made lowercase.
    ispublished = models.BooleanField(db_column='isPublished')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'WebsiteAcademyModule'


class Websiteleader(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    role = models.TextField()
    bio = models.TextField()
    photourl = models.TextField(db_column='photoUrl')  # Field name made lowercase.
    sortorder = models.IntegerField(db_column='sortOrder')  # Field name made lowercase.
    social = models.JSONField(blank=True, null=True)
    ispublished = models.BooleanField(db_column='isPublished')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'WebsiteLeader'


class Websitetestimonial(models.Model):
    id = models.TextField(primary_key=True)
    quote = models.TextField()
    name = models.TextField()
    role = models.TextField(blank=True, null=True)
    photourl = models.TextField(db_column='photoUrl', blank=True, null=True)  # Field name made lowercase.
    sortorder = models.IntegerField(db_column='sortOrder')  # Field name made lowercase.
    ispublished = models.BooleanField(db_column='isPublished')  # Field name made lowercase.
    createdat = models.DateTimeField(db_column='createdAt')  # Field name made lowercase.
    updatedat = models.DateTimeField(db_column='updatedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'WebsiteTestimonial'
