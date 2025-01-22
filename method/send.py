from gdo.base.Cache import Cache
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.core.GDT_User import GDT_User
from gdo.date.Time import Time
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.mail.Mail import Mail
from gdo.message.GDT_Message import GDT_Message
from gdo.pm.module_pm import module_pm
from gdo.pm.GDO_PM import GDO_PM
from gdo.ui.GDT_Title import GDT_Title


class send(MethodForm):

    def gdo_trigger(self) -> str:
        return 'pm.send'

    def gdo_user_type(self) -> str | None:
        return 'member,ghost'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(
            GDT_User('to').not_null(),
            GDT_Title('title').not_null(),
        )
        if self._env_http:
            form.add_field(GDT_Message('message').not_null())
        else:
            form.add_field(GDT_RestOfText('message').not_null())
        super().gdo_create_form(form)

    def form_submitted(self) -> GDT:
        sender = self._env_user
        target = self.param_value('to') # type: GDO_User
        title = self.param_value('title')
        message = self.param_value('message')
        self.send_pm(sender, target, title, message)
        return self.reply('msg_pm_sent', (target.render_name(),))

    def send_pm(self, sender: GDO_User, target: GDO_User, title: str, message: str):
        self.create_pm(sender, target, title, message, sender, True)
        pm = self.create_pm(sender, target, title, message, target, False)
        Cache.remove('new_pm_count', target.get_id())
        if module_pm.instance().cfg_welcome_pm():
            self.send_email(pm)

    def create_pm(self, sender: GDO_User, target: GDO_User, title: str, message: str, owner: GDO_User, mark_read: bool):
        return GDO_PM.blank({
            'pm_folder': '1' if target == owner else '2',
            'pm_from': sender.get_id(),
            'pm_to': target.get_id(),
            'pm_owner': owner.get_id(),
            'pm_title': title,
            'pm_message': self.get_message(message, owner),
            'pm_read': Time.get_date() if mark_read else None,
            'pm_encrypted': self.get_encrypted(owner),
        }).insert()

    def get_message(self, message: str, user: GDO_User) -> str:
        return message

    def get_encrypted(self, user: GDO_User) -> str:
        return '0'

    def send_email(self, pm: GDO_PM):
        mail = Mail.from_bot()

