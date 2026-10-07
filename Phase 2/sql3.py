from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(20), primary_key=True)
    gender = Column(String(10))
    senior_citizen = Column(Integer)
    partner = Column(Integer)
    dependents = Column(Integer)

    def __repr__(self):
        return (
            f"Customer("
            f"customer_id='{self.customer_id}', "
            f"gender='{self.gender}', "
            f"senior_citizen={self.senior_citizen}, "
            f"partner={self.partner}, "
            f"dependents={self.dependents})"
        )


class Contract(Base):
    __tablename__ = "dim_contract"

    contract_key = Column(Integer, primary_key=True)
    contract_name = Column(String(50))

    def __repr__(self):
        return (
            f"Contract("
            f"contract_key={self.contract_key}, "
            f"contract_name='{self.contract_name}')"
        )

engine = create_engine(
    "mysql+pymysql://root:root@localhost/friday"
)

Session = sessionmaker(bind=engine)
session = Session()

customer = (
    session.query(Customer)
    .filter(Customer.customer_id == "7590-VHVEG")
    .first()
)

print("Query Result:", customer)

if customer is not None:
    print("Customer ID:", customer.customer_id)
    print("Gender:", customer.gender)
    print("Partner:", customer.partner)
    print("Dependents:", customer.dependents)
else:
    print("Customer not found!")

session.close()