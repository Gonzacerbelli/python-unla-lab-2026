from datetime import date

from fastapi import FastAPI, status, HTTPException, Query
from sqlalchemy import func
from database import db_session, Products, Sales, Carts, CartItems
from schema import (
    ProductCreate,
    CartCreate,
    CartItemCreate,
    CartResponse,
    SaleCreate,
    SaleUpdate,
    SaleCartAssign,
    SaleResponse,
)

app = FastAPI()


@app.middleware("http")
def close_db_session(request, call_next):
    response = call_next(request)
    db_session.remove()
    return response


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/products", status_code=status.HTTP_200_OK)
def get_products():
    try:
        products = Products.query.all()
        response = {"products": products}
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get products: {e}")


@app.get("/products/best-sellers", status_code=status.HTTP_200_OK)
def get_best_sellers():
    try:
        products = (
            Products.query
            .join(CartItems)
            .group_by(Products.id)
            .order_by(func.sum(CartItems.quantity).desc())
            .limit(5)
            .all()
        )
        response = {"products": products}
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get best-selling products: {e}")


@app.get("/products/{product_id}", status_code=status.HTTP_200_OK)
def get_product(product_id: int):
    try:
        product = Products.query.get(product_id)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        
        response = {"product": product}
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get product with id {product_id}: {e}")


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate):
    try:
        product = Products.query.filter_by(name=product_data.name).first()

        if product:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already exists")
        
        product = Products(
            name=product_data.name,
            price=product_data.price
        )

        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        response = {"product": product}
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to create product: {e}")


@app.put("/products/{product_id}", status_code=status.HTTP_200_OK)
def update_product(product_id: int, product_data: ProductCreate):
    try:
        product = Products.query.get(product_id)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        existing_product = Products.query.filter(Products.name == product_data.name, Products.id != product_id).first()

        if existing_product:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already exists")

        product.name = product_data.name
        product.price = product_data.price

        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        response = {"product": product}
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to update product with id {product_id}: {e}")


@app.delete("/products/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int):
    try:
        product = Products.query.get(product_id)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        if product.cart_items:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product cannot be deleted because it is registered in a cart"
            )

        db_session.delete(product)
        db_session.commit()

        return {"message": "Product deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to delete product with id {product_id}: {e}")


@app.get("/carts", status_code=status.HTTP_200_OK, response_model=list[CartResponse])
def get_carts():
    try:
        carts = Carts.query.all()
        return carts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get carts: {e}")


@app.get("/carts/{cart_id}", status_code=status.HTTP_200_OK, response_model=CartResponse)
def get_cart(cart_id: int):
    try:
        cart = Carts.query.get(cart_id)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        return cart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get cart with id {cart_id}: {e}")


@app.post("/carts", status_code=status.HTTP_201_CREATED, response_model=CartResponse)
def create_cart(cart_data: CartCreate):
    try:
        cart = Carts(
            creation_date=cart_data.creation_date,
            status=cart_data.status
        )

        db_session.add(cart)
        db_session.commit()
        db_session.refresh(cart)

        return cart
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to create cart: {e}")


@app.put("/carts/{cart_id}", status_code=status.HTTP_200_OK, response_model=CartResponse)
def update_cart(cart_id: int, cart_data: CartCreate):
    try:
        cart = Carts.query.get(cart_id)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        if cart.sales:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cart cannot be modified because it is assigned to a sale"
            )

        cart.creation_date = cart_data.creation_date
        cart.status = cart_data.status

        db_session.add(cart)
        db_session.commit()
        db_session.refresh(cart)

        return cart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to update cart with id {cart_id}: {e}")


@app.delete("/carts/{cart_id}", status_code=status.HTTP_200_OK)
def delete_cart(cart_id: int):
    try:
        cart = Carts.query.get(cart_id)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        if cart.sales:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cart cannot be deleted because it is assigned to a sale"
            )

        db_session.delete(cart)
        db_session.commit()

        return {"message": "Cart deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to delete cart with id {cart_id}: {e}")


@app.post("/carts/{cart_id}/products", status_code=status.HTTP_201_CREATED, response_model=CartResponse)
def add_product_to_cart(cart_id: int, cart_item_data: CartItemCreate):
    try:
        cart = Carts.query.get(cart_id)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        if cart.status != "open":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Products can only be added to a cart with status 'open'"
            )

        product = Products.query.get(cart_item_data.product_id)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist")

        if cart_item_data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than 0"
            )

        cart_item = CartItems.query.filter_by(cart_id=cart.id, product_id=product.id).first()

        if cart_item:
            cart_item.quantity += cart_item_data.quantity
        else:
            cart_item = CartItems(
                cart_id=cart.id,
                product_id=product.id,
                quantity=cart_item_data.quantity
            )
            db_session.add(cart_item)

        db_session.commit()
        db_session.refresh(cart)

        return cart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to add product to cart with id {cart_id}: {e}")


@app.delete("/carts/{cart_id}/products/{product_id}", status_code=status.HTTP_200_OK, response_model=CartResponse)
def remove_product_from_cart(cart_id: int, product_id: int):
    try:
        cart = Carts.query.get(cart_id)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        if cart.status != "open":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Products can only be removed from a cart with status 'open'"
            )

        cart_item = CartItems.query.filter_by(cart_id=cart.id, product_id=product_id).first()

        if not cart_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product is not registered in the cart")

        db_session.delete(cart_item)
        db_session.commit()
        db_session.refresh(cart)

        return cart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to remove product from cart with id {cart_id}: {e}")


@app.get("/sales", status_code=status.HTTP_200_OK, response_model=list[SaleResponse])
def get_sales(
    date_from: date | None = Query(None, alias="date-from"),
    date_to: date | None = Query(None, alias="date-to")
):
    try:
        if date_from and date_to and date_from > date_to:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="date-from must be before or equal to date-to")

        query = Sales.query

        if date_from:
            query = query.filter(Sales.date >= date_from)

        if date_to:
            query = query.filter(Sales.date <= date_to)

        sales = query.all()
        return sales
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get sales: {e}")


@app.get("/sales/most-profitable", status_code=status.HTTP_200_OK, response_model=list[SaleResponse])
def get_most_profitable_sales():
    try:
        sales = Sales.query.order_by(Sales.total_price.desc()).limit(5).all()
        return sales
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get most profitable sales: {e}")


@app.get("/sales/{sale_id}", status_code=status.HTTP_200_OK, response_model=SaleResponse)
def get_sale(sale_id: int):
    try:
        sale = Sales.query.get(sale_id)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
        
        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get sale with id {sale_id}: {e}")


@app.post("/sales", status_code=status.HTTP_201_CREATED, response_model=SaleResponse)
def create_sale(sale_data: SaleCreate):
    try:
        cart = Carts.query.get(sale_data.cart_id)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart does not exist")

        if cart.status != "close":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only carts with status 'close' can be assigned to a sale"
            )

        if Sales.query.filter_by(cart_id=cart.id).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cart is already assigned to another sale"
            )

        # sacar total price del post y llevarlo solo al get
        total_price = sum(item.quantity * item.product.price for item in cart.items)

        sale = Sales(
            date=sale_data.date,
            time=sale_data.time,
            cart_id=cart.id,
            total_price=total_price
        )

        db_session.add(sale)
        db_session.commit()
        db_session.refresh(sale)

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to create sale: {e}")


@app.post("/sales/{sale_id}/cart", status_code=status.HTTP_200_OK, response_model=SaleResponse)
def assign_cart_to_sale(sale_id: int, sale_cart_data: SaleCartAssign):
    try:
        sale = Sales.query.get(sale_id)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        cart = Carts.query.get(sale_cart_data.cart_id)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart does not exist")

        if cart.status != "close":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only carts with status 'close' can be assigned to a sale"
            )

        if Sales.query.filter(Sales.cart_id == cart.id, Sales.id != sale_id).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cart is already assigned to another sale"
            )

        sale.cart_id = cart.id
        sale.total_price = sum(item.quantity * item.product.price for item in cart.items)

        db_session.add(sale)
        db_session.commit()
        db_session.refresh(sale)

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to assign cart to sale with id {sale_id}: {e}")


@app.put("/sales/{sale_id}", status_code=status.HTTP_200_OK, response_model=SaleResponse)
def update_sale(sale_id: int, sale_data: SaleUpdate):
    try:
        sale = Sales.query.get(sale_id)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        sale.date = sale_data.date
        sale.time = sale_data.time

        db_session.add(sale)
        db_session.commit()
        db_session.refresh(sale)

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to update sale with id {sale_id}: {e}")


@app.delete("/sales/{sale_id}", status_code=status.HTTP_200_OK)
def delete_sale(sale_id: int):
    try:
        sale = Sales.query.get(sale_id)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        db_session.delete(sale)
        db_session.commit()

        return {"message": "Sale deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to delete sale with id {sale_id}: {e}")