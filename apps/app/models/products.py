from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from app import db



# Product Group
# depth of the product group can be determined from relationship from root. Has to be enforced from 


 
class ProductGroupMap ( db.Model ):
    __tablename__ = 'productgroup_map'
    product_id = Column ( Integer, primary_key = True )
    group_id  = Column ( Integer, primary_key = True )
    
class Product(db.Model):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key = True)
    extref_id = Column(String)
    name = Column(String)
    
    #productgroup_map = relationship('ProductGroupMap')

    
# Define additional custom column for products.
class ProductSchema(db.Model):
    __tablename__ = 'product_schema'
    id = Column(Integer, primary_key = True)
    name = Column(String)
    data_type = Column(Integer)

class ProductSchema_DataType:
    Integer = 0
    String = 1
    Double = 2

# define the data for the specific column of products
class ProductCustomData (db.Model):
    __tablename__ = 'product_custom_data'
    
    id = Column(Integer, primary_key = True)
    schema_id = Column(Integer, ForeignKey('product_schema.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    data = Column(String)

class ProductGroup(db.Model):
    __tablename__ = 'product_group'
    
    id = Column (Integer, primary_key = True)
    parent_id = Column (Integer, nullable = True)
    extref_id = Column (String)
    description = Column (String)

    @property
    def GroupChildren(self):
        return ProductGroup.query.filter_by(parent_id = self.id)
        
    @property
    def GroupParent(self):
        try:
            return ProductGroup.query.get(id = self.parent_id)
        except:
            return None
    @property
    def ChildProducts(self):
        return db.session.query(ProductGroupMap).outerjoin(Product, ProductGroupMap.product_id == Product.id).filter(ProductGroupMap.group_id == self.id).add_entity(Product)
 