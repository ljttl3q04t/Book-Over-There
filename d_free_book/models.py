from django.db import models

from services.models import BaseModel, Book, BookClub, Membership


class ClubBook(BaseModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, db_index=True)
    club = models.ForeignKey(BookClub, on_delete=models.CASCADE)
    init_count = models.IntegerField(null=True, blank=True)
    current_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.id} - {self.code}'

    class Meta:
        db_table = 'dfree_book_tab'
        # unique_together = ['code', 'club']

class DFreeMember(BaseModel):
    club = models.ForeignKey(BookClub, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f'{self.id} - {self.club_id} - {self.code} - {self.full_name}'

    class Meta:
        db_table = 'dfree_member_tab'

class DFreeOrder(BaseModel):
    member = models.ForeignKey(DFreeMember, on_delete=models.CASCADE)
    club = models.ForeignKey(BookClub, on_delete=models.CASCADE)
    order_date = models.DateField()
    due_date = models.DateField()
    creator_order = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'dfree_order_tab'

class DFreeOrderDetail(BaseModel):
    CREATED = 'created'
    OVERDUE = 'overdue'
    COMPLETE = 'complete'
    ORDER_STATUS_CHOICES = (
        (CREATED, 'Created'),
        (OVERDUE, 'Overdue'),
        (COMPLETE, 'Complete'),
    )

    order = models.ForeignKey(DFreeOrder, on_delete=models.CASCADE)
    club_book = models.ForeignKey(ClubBook, on_delete=models.CASCADE, null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    overdue_day_count = models.IntegerField(null=True, blank=True)
    note = models.CharField(max_length=200, blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=CREATED)
    receiver = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'dfree_order_detail_tab'
