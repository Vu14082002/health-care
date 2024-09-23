import socketio
import engineio


class _BaseAsyncNameSpace(socketio.AsyncNamespace):
    def __init__(self, namespace: str = ""):
        if not namespace.startswith("/"):
            namespace = f"/{namespace}"
        if namespace.endswith("/"):
            namespace = namespace[:-1]
        self.namespace = namespace
        super().__init__(namespace)

    async def on_connect(self, sid, environ):
        # logger.info("Conected: ")
        pass

    async def on_disconnect(self, sid):
        # logger.info("Disconected: ")
        pass

    def on_error(self, *args):
        logger.info(args)


class SocketIoServer:

    def __init__(self) -> None:
        self.sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
        self.app = None
        self.sio.register_namespace(_BaseAsyncNameSpace("/"))

    def route(
        self,
        path: str = "test",
        name_space=_BaseAsyncNameSpace,
        *args,
        **kwargs,
    ) -> None:
        self.sio.register_namespace(name_space(path))

    def get_application(self, socket_path="socket.io"):
        return engineio.ASGIApp(engineio_server=self.sio, engineio_path=socket_path)

    @property
    def NameSpace(self):
        return _BaseAsyncNameSpace
