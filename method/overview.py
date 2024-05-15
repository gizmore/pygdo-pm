from gdo.base.Method import Method


class overview(Method):

    def gdo_user_type(self) -> str | None:
        return 'member,guest,link'
