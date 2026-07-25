class ProductAlreadyExistsError(Exception):
    def __init__(self, product_name: str):
        self.product_name = product_name
        super().__init__(f'Product "{product_name}" has already been added')
