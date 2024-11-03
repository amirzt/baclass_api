from fcm_django.admin import FCMDevice
from firebase_admin.messaging import Message, Notification


def senf_fcm(user, title, body):
    # initialize_app()
    # FCMDevice.objects.send_message(Message(data=dict()))
    #
    # FCMDevice.objects.send_message(
    #     Message(notification=Notification(title="title", body="body", image="image_url"))
    # )
    # device = FCMDevice.objects.first()
    # device.send_message(Message(...))

    # notification
    notification = Message(
        notification=Notification(title="title", body="text", image="url"),
        topic="Optional topic parameter: Whatever you want",
    )

    # data message
    message = Message(
        data={"key": "value"},
        topic="Optional topic parameter: Whatever you want",
    )
    print(user.phone)
    device = FCMDevice.objects.filter(user=user).first()

    if device:
        device.send_message(notification)
