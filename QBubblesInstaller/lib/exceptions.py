class SceneNotFoundError(Exception):
    __name__ = "SceneNotFoundError"

    def __init__(self, *args: object):
        self.__class__.__name__ = "SceneNotFoundError"
        super(SceneNotFoundError, self).__init__(*args)

    def __repr__(self):
        return self.__class__.__name__
