from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import(
                Column, 
                Integer, 
                Boolean,
                String, 
                ForeignKey, 
                create_engine
                )
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()
class Category(Base):
    __tablename__ = "category"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    
    record = relationship("Record", back_populates="category")
    
    def __str__(self):
        return self.name
        
        
class Record(Base):
    __tablename__ = "record"
    id = Column(Integer, primary_key=True)
    text = Column(String(100))
    status = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey("category.id"))
    
    category = relationship("Category", back_populates="record")
    
engine = create_engine("sqlite:///org.db")
Base.metadata.create_all(engine)
