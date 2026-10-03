from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import t
from gdo.core.GDT_Object import GDT_Object
from gdo.date.Time import Time
from gdo.language.GDT_Trans import GDT_Trans
from gdo.pm.GDO_PM import GDO_PM
from gdo.ui.GDT_Card import GDT_Card


class view(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'pm.read'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_Object('id').table(GDO_PM.table()).positional(),
        ]

    def get_pm(self) -> GDO_PM | None:
        return self.param_value('id')

    def gdo_execute(self) -> GDT:
        pm = self.get_pm()
        if pm is None:
            pm = self.get_unread_pm()
            if pm is None:
                return self.msg('msg_no_more_new_pm')
        if pm.get_owner() != self._env_user:
            return self.err('err_permission', (t('owner'),))
        if pm.gdo_val('pm_read') is None:
            pm.save_val('pm_read', Time.get_date())
            GDO_PM.clear_unread_count(self._env_user)
        card = GDT_Card().gdo(pm).add_class('pm-read-card')
        card.title_raw(pm.render_title())
        # A private message is viewed from its owner's perspective. Show the
        # counterpart once, labelled by the meaningful direction.
        card.get_header().add_field(
            pm.column(pm.get_other_user_key(self._env_user)))
        card.get_content().add_fields(pm.column('pm_message'))
        created = pm.column('pm_created')
        card.get_footer().add_field(
            GDT_Trans().text_raw(
                f'{created.render_format(Time.FMT_SHORT)} '
                f'({created.render_format(Time.FMT_AGO)})'))
        return card

    def get_unread_pm(self) -> GDO_PM | None:
        return (GDO_PM.table().select().where(
            f"pm_owner={self._env_user.get_id()} AND pm_read IS NULL"
        ).first().order('pm_created ASC').exec().fetch_object())
