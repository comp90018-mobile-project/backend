from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import socketio

sio = socketio.Server(async_mode='gevent')
thread = None


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        sio.sleep(10)
        count += 1
        sio.emit('my_response', {'data': 'Server generated event'},
                 namespace='/test')


@sio.on("createEvent")
def create_event(event, sid, data: dict):
    print(event, sid, data)
    sio.emit('getEvents', {'data': 'someone creates an event!'})


@sio.on("cancelEvent")
def cancel_event(event, sid, data: dict):
    print(event, sid, data)
    sio.emit('getEvents', {'data': 'someone cancels an event!'})


@sio.on("modifyEvent")
def modify_event(event, sid, data: dict):
    print(event, sid, data)
    sio.emit('getEvents', {'data': 'someone modifies an event!'})


@sio.event
def connect(sid, environ):
    print(f"client connected with sid {sid}")
    sio.emit('connect', {'data': 'Connected', 'count': 0}, room=sid)


@sio.event
def disconnect(sid):
    print('Client disconnected')


#
@csrf_exempt
def events1(request: HttpRequest):
    global thread
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return JsonResponse(
        data={"msg": "socket OK"}
    )
