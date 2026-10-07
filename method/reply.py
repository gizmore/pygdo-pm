from gdo.base.GDT import GDT
from gdo.core.GDT_Object import GDT_Object
from gdo.pm.GDO_PM import GDO_PM
from gdo.pm.method.send import send


class reply(send):
    """Reply to one PM while preserving its parent for thread navigation."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'pm.reply'

    def gdo_parameters(self) -> list[GDT]:
        return [GDT_Object('id').table(GDO_PM.table()).not_null().positional()]

    def get_pm(self) -> GDO_PM:
        return self.param_value('id')

    def gdo_execute(self) -> GDT:
        if self.get_pm().get_owner() != self._env_user.get_effective_user():
            return self.err('err_permission', ('owner',))
        return super().gdo_execute()

    def gdo_create_form(self, form):
        pm = self.get_pm()
        super().gdo_create_form(form)
        form.get_field('to').initial_value(pm.get_other_user(self._env_user)).disabled()
        form.get_field('parent').initial(pm.get_id())
        form.get_field('title').initial(f'Re: {pm.render_title()}')

    def form_submitted(self) -> GDT:
        pm = self.get_pm()
        title = self.param_value('title')
        message = self.param_value('message_input') if self._env_http else self.param_value('message')
        sender = self._env_reply_to or self._env_user
        self.send_pm(sender, pm.get_other_user(self._env_user), title, message, pm)
        return self.reply('msg_pm_sent', (pm.get_other_user(self._env_user).render_name(),))
