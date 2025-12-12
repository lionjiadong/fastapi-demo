# from .role import RoleOut, RoleOutLinks
from .department import DepartmentOut, DepartmentOutLinks
from .user import UserOut, UserOutLinks

# RoleOut.model_rebuild()
UserOut.model_rebuild()
DepartmentOut.model_rebuild()
DepartmentOutLinks.model_rebuild()
UserOutLinks.model_rebuild()
# RoleOutLinks.model_rebuild()
# UserOutLinks.model_rebuild()
