from typing import Callable, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

# repos
from app.repos.user_repo import UserRepo
from app.repos.partner_repo import PartnerRepo
from app.repos.category_repo import CategoryRepo
from app.repos.currency_repo import CurrencyRepo
from app.repos.product_repo import ProductRepo
from app.repos.receipt_item_repo import ReceiptItemRepo
from app.repos.receipt_repo import ReceiptRepo
from app.repos.writeoff_repo import WriteOffRepo
from app.repos.writeoff_item_repo import WriteOffItemRepo
from app.repos.sale_repo import SaleRepo
from app.repos.sale_item_repo import SaleItemRepo

# controllers
from app.controllers.user_controller import UserController
from app.controllers.partner_controller import PartnerController
from app.controllers.category_controller import CategoryController
from app.controllers.currency_controller import CurrencyController
from app.controllers.product_controller import ProductController
from app.controllers.receipt_controller import ReceiptController
from app.controllers.writeoff_controller import WriteOffController
from app.controllers.sale_controller import SaleController


TRepo = TypeVar("TRepo")
TCtrl = TypeVar("TCtrl")


def get_repo(repo_class: type[TRepo]) -> Callable[[AsyncSession], TRepo]:
    def _get_repo(session: AsyncSession = Depends(get_session)) -> TRepo:
        return repo_class(session)  # type: ignore[misc]
    return _get_repo


def get_controller(controller_class: type[TCtrl], repo_dependency) -> Callable[..., TCtrl]:
    def _get_controller(repo=Depends(repo_dependency)) -> TCtrl:
        return controller_class(repo)  # type: ignore[misc]
    return _get_controller


# repo factories
get_user_repo = get_repo(UserRepo)
get_partner_repo = get_repo(PartnerRepo)
get_category_repo = get_repo(CategoryRepo)
get_currency_repo = get_repo(CurrencyRepo)
get_product_repo = get_repo(ProductRepo)

# controller factories
get_user_controller = get_controller(UserController, get_user_repo)
get_partner_controller = get_controller(PartnerController, get_partner_repo)
get_category_controller = get_controller(CategoryController, get_category_repo)
get_currency_controller = get_controller(CurrencyController, get_currency_repo)


def get_product_controller(
    session: AsyncSession = Depends(get_session),
) -> ProductController:
    return ProductController(
        session=session,
        repo=ProductRepo(session),
        currency_repo=CurrencyRepo(session),
        category_repo=CategoryRepo(session),
    )

def get_receipt_controller(session: AsyncSession = Depends(get_session)) -> ReceiptController:
    return ReceiptController(
        session=session,
        receipt_repo=ReceiptRepo(session),
        receipt_item_repo=ReceiptItemRepo(session),
        product_repo=ProductRepo(session),
        partner_repo=PartnerRepo(session),
        currency_repo=CurrencyRepo(session),
        category_repo=CategoryRepo(session),
    )

def get_writeoff_controller(session: AsyncSession = Depends(get_session)) -> WriteOffController:
    return WriteOffController(
        session=session,
        writeoff_repo=WriteOffRepo(session),
        writeoff_item_repo=WriteOffItemRepo(session),
        product_repo=ProductRepo(session),
        partner_repo=PartnerRepo(session),
    )



def get_sale_controller(session=Depends(get_session)) -> SaleController:
    return SaleController(
        session=session,
        partner_repo=PartnerRepo(session),
        product_repo=ProductRepo(session),
        sale_repo=SaleRepo(session),
        sale_item_repo=SaleItemRepo(session),
    )