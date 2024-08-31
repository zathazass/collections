from collections import namedtuple
from rest_framework.request import Request


Value = namedtuple(
    "Value", ["required", "blank", "null", "cast"], defaults=[False, True, True, str]
)


class RequestHandler:
    default_raise_exception = False
    default_error_list = False
    default_omit = True

    def __init__(
        self,
        request: Request,
        query_convertors: dict = {},
        data_convertors: dict = {},
        **kwargs,
    ):

        self.__req = request
        self._query_convertors = query_convertors
        self._data_convertors = data_convertors

        self.raise_exception = kwargs.get(
            "raise_exception", self.default_raise_exception
        )
        self.error_list = kwargs.get("error_list", self.default_error_list)
        self.omit = kwargs.get("omit", self.default_omit)

        self.error_message = [] if self.error_list else ""
        self.error_dict = {}
        self.params = self._params()
        self.data = self._data()

    @property
    def request(self):
        return self.__req

    @property
    def headers(self):
        return self.__req.headers

    @property
    def user(self):
        return self.__req.user

    def _params(self):
        return self._convert_data(
            self.__req.query_params.dict(), self._query_convertors
        )

    def _data(self):
        if self.__req.content_type == "application/json":
            value = self.__req.data
        else:
            value = self.__req.data.dict()
        return self._convert_data(value, self._data_convertors)

    @property
    def files(self):
        return self.__req.FILES.dict()

    @property
    def query_convertors(self):
        return self._query_convertors

    @property
    def data_convertors(self):
        return self._data_convertors

    def __bool__(self):
        return not bool(self.error_message)

    def _convert_data(self, data: dict, convertor):
        self._handle_required(data, convertor)

        result = {}
        if convertor:
            for key, value in data.items():
                if self.error_message and not self.error_list:
                    break

                if key not in convertor:
                    if not self.omit:
                        result[key] = value
                    continue

                val: Value = convertor[key]
                if self._as_null(val, key, data, result):
                    continue

                if self._as_blank(val, key, data, result):
                    continue

                self._cast(val, key, data, result)

            return result
        return data

    def _as_null(self, val: Value, key, data, result):
        result[key] = None if val.null else data[key]

        if not data[key] in ["null", None]:
            return False

        if val.required or not val.null:
            self._handle_error(key, f"The value for '{key}' should not be null.")

        return True

    def _as_blank(self, val: Value, key, data, result):
        result[key] = "" if val.blank else data[key]

        if not (isinstance(data[key], str) and data[key].strip() == ""):
            return False

        if val.required or not val.blank:
            self._handle_error(key, f"The value for '{key}' should not be blank.")

        return True

    def _cast(self, val: Value, key, data, result):
        try:
            result[key] = val.cast(data[key])
        except (ValueError, TypeError) as e:
            self._handle_error(
                key,
                f"Failed to convert the value of '{key}' using {val.cast.__name__}. Error: {e}",
            )

    def _handle_required(self, data: dict, convertor: dict):
        for key, val in convertor.items():
            if val.required and key not in data:
                self._handle_error(key, f"{key} is required.")

    def _handle_error(self, key: str, message: str):
        message = message.capitalize().replace("_", " ")

        if self.raise_exception:
            raise ValueError(message)
        else:
            if self.error_list:
                self.error_message.append(message)
            else:
                self.error_message = message
            self.error_dict[key] = message
