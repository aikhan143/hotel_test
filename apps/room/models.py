from django.db import models

class Room(models.Model):
    room_statuses = [
        ('Free', 'Free'),
        ('Busy', 'Busy'),
        ('Reserved', 'Reserved')
    ]
    room_status = models.CharField(max_length=8, choices=room_statuses, default='Free', blank=True)
    room_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    preview = models.ImageField(upload_to='previews/')

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'

    def __str__(self):
        return f'{self.number} (rooms:{self.room_count})'

class RoomImage(models.Model):
    image = models.ImageField(upload_to='rooms-img/')
    rooms = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
