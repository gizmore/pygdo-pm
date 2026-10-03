from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import t
from gdo.core.GDT_Object import GDT_Object
from gdo.date.Time import Time
from gdo.language.GDT_Trans import GDT_Trans
from gdo.pm.GDO_PM import GDO_PM
from gdo.ui.GDT_Card import GDT_Card
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Menu import GDT_Menu


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
        card.get_footer().add_field(self.render_navigation(pm))
        return card

    def render_navigation(self, pm: GDO_PM) -> GDT_Menu:
        """Offer the next useful PM action without leaving the reading flow."""
        follow_up = self.get_follow_up_pm(pm)
        prev_thread = self.get_prev_thread_pm(pm)
        next_thread = self.get_next_thread_pm(pm)
        return GDT_Menu().horizontal().add_fields(
            GDT_Link().href(self.gdo_module().href(
                'reply', f'&id={pm.get_id()}'
            )).text('link_pm_reply').icon('reply'),
            GDT_Link().href(self.gdo_module().href(
                'view', f'&id={follow_up.get_id() if follow_up else 0}'
            )).text('link_pm_follow_up').icon('forward').disabled(follow_up is None),
            GDT_Link().href(self.gdo_module().href(
                'view', f'&id={prev_thread.get_id() if prev_thread else 0}'
            )).text('link_pm_prev_thread').icon('backward').disabled(prev_thread is None),
            GDT_Link().href(self.gdo_module().href(
                'view', f'&id={next_thread.get_id() if next_thread else 0}'
            )).text('link_pm_next_thread').icon('forward').disabled(next_thread is None),
        )

    def get_unread_pm(self) -> GDO_PM | None:
        return (GDO_PM.table().select().where(
            f"pm_owner={self._env_user.get_id()} AND pm_read IS NULL"
        ).first().order('pm_created ASC').exec().fetch_object())

    def get_next_thread_pm(self, pm: GDO_PM) -> GDO_PM | None:
        """Return the next newer root PM."""
        return (GDO_PM.table().select().where(
            f'pm_owner={self._env_user.get_id()} AND pm_parent IS NULL AND pm_id>{pm.get_id()}'
        ).first().order('pm_id ASC').exec().fetch_object())

    def get_prev_thread_pm(self, pm: GDO_PM) -> GDO_PM | None:
        """Return the previous (older) root PM."""
        return (GDO_PM.table().select().where(
            f'pm_owner={self._env_user.get_id()} AND pm_parent IS NULL AND pm_id<{pm.get_id()}'
        ).first().order('pm_id DESC').exec().fetch_object())

    def get_follow_up_pm(self, pm: GDO_PM) -> GDO_PM | None:
        """Return the first reply belonging to this PM in the owner's thread."""
        return (GDO_PM.table().select().where(
            f'pm_owner={self._env_user.get_id()} AND pm_parent={pm.get_id()}'
        ).first().order('pm_id ASC').exec().fetch_object())
