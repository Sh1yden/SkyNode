from fastapi import Request
from sqladmin import Admin, ModelView, BaseView, action, expose
from common.database.models import UserAllInfo, WeatherAllInfo


class HomeView(BaseView):
    name = "Home"
    icon = "fa-solid fa-house"

    @expose("/custom", methods=["GET"])
    async def test_page(self, request: Request):
        return await self.templates.TemplateResponse(request, "custom.html")


class UserAdmin(ModelView, model=UserAllInfo):
    category = "Users and Activity"
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = "__all__"
    column_sortable_list = column_list
    column_searchable_list = column_list
    form_columns = column_list
    column_default_sort = [(UserAllInfo.id, True), (UserAllInfo.user_id, True)]

    # TODO \/
    # @action(name="Send Message to User")
    # async def send_test_message_to_user():
    #     pass

    can_export = True
    export_types = ["json", "csv", "xls"]


class WeatherAdmin(ModelView, model=WeatherAllInfo):
    category = "Weather"
    name = "Weather"
    name_plural = "Weather"
    icon = "fa-solid fa-cloud-sun"

    column_list = "__all__"
    column_sortable_list = column_list
    column_searchable_list = column_list
    form_columns = column_list
    column_default_sort = [(WeatherAllInfo.id, True)]

    can_export = True
    export_types = ["json", "csv", "xls"]


async def setup_admin(app, engine):
    admin = Admin(app=app, engine=engine)

    admin.add_base_view(HomeView)
    admin.add_view(UserAdmin)
    admin.add_view(WeatherAdmin)
