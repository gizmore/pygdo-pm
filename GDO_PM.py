from gdo.base.Cache import Cache
from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_UInt import GDT_UInt
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Created import GDT_Created
from gdo.date.GDT_Timestamp import GDT_Timestamp
from gdo.message.GDT_Message import GDT_Message
from gdo.pm.GDT_PMFolder import GDT_PMFolder
from gdo.ui.GDT_Title import GDT_Title

class GDO_PM(GDO):

    def gdo_cached(self) -> bool:
        return False

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('pm_id'),
            # A self-reference is stored as an ID.  Keeping this as an UInt
            # avoids recursive schema construction while still permitting
            # lightweight PM thread navigation.
            GDT_UInt('pm_parent'),
            GDT_PMFolder('pm_folder').label('folder').not_null().cascade_delete(),
            GDT_User('pm_from').label('from').not_null(),
            GDT_User('pm_to').label('to').not_null().cascade_delete(),
            GDT_User('pm_owner').label('owner').not_null().cascade_delete(),
            GDT_Title('pm_title').not_null(),
            GDT_Message('pm_message').not_null(),
            GDT_Bool('pm_encrypted').not_null(),
            GDT_Timestamp('pm_read'),
            GDT_Created('pm_created'),
        ]

    def get_owner(self) -> GDO_User:
        return self.gdo_value('pm_owner')

    def get_parent(self) -> 'GDO_PM | None':
        parent_id = self.gdo_val('pm_parent')
        return self.table().get_by_aid(parent_id) if parent_id else None

    def render_title(self) -> str:
        return self.gdo_val('pm_title')

    def is_unread(self) -> bool:
        return self.gdo_value('pm_read') is None

    def get_other_user_key(self, user: GDO_User) -> str:
        """Return the counterpart without losing linked connector identities."""
        if user.get_id() == self.gdo_val('pm_to'):
            return 'pm_from'
        if user.get_id() == self.gdo_val('pm_from'):
            return 'pm_to'
        # A linked account stores its PMs under the master account.  The
        # mailbox folder still unambiguously tells which concrete user is on
        # the other side of the conversation.
        return 'pm_from' if self.gdo_val('pm_folder') == '1' else 'pm_to'

    def get_other_user(self, user: GDO_User) -> GDO_User:
        return self.gdo_value(self.get_other_user_key(user))

    @classmethod
    def unread_count(cls, user: GDO_User) -> str:
        user = user.get_effective_user()
        if (cached := Cache.get('new_pm_count', user.get_id())) is not None:
            return cached
        count = str(cls.table().count_where(f'pm_owner={user.get_id()} AND pm_read IS NULL')) or '0'
        Cache.set('new_pm_count', user.get_id(), count)
        return count

    @classmethod
    def clear_unread_count(cls, user: GDO_User) -> None:
        user = user.get_effective_user()
        Cache.remove('new_pm_count', user.get_id())
