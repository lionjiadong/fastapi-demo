from .role import RoleOut, RoleOutLinks
from .user import UserOut, UserOutLinks

RoleOut.model_rebuild()
UserOut.model_rebuild()
RoleOutLinks.model_rebuild()
UserOutLinks.model_rebuild()
