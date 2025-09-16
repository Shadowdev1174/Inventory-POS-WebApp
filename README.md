# Inventory & Point of Sale (POS) System

A modern, customizable inventory and point of sale management system built with Django and Tailwind CSS. This application is designed to be easily customizable for different clients and business needs.

## Features

### 🏪 **Inventory Management**
- **Product Management**: Add, edit, delete products with images, pricing, and stock tracking
- **Category Management**: Organize products into categories
- **Supplier Management**: Track suppliers and their contact information
- **Stock Tracking**: Real-time stock levels with low stock alerts
- **Stock Movements**: Track all stock in/out movements with reasons and references
- **Barcode Support**: SKU and barcode management for products

### 💰 **Point of Sale (POS)**
- **Modern POS Interface**: User-friendly checkout system
- **Shopping Cart**: Add/remove products with quantity adjustments
- **Customer Management**: Track customer information and purchase history
- **Multiple Payment Methods**: Cash, Card, Check, Mobile payments
- **Receipt Generation**: Printable receipts with company branding
- **Sales Tracking**: Complete sales history and reporting
- **Refund Management**: Handle returns and refunds

### 👥 **User Management & Security**
- **Role-Based Access Control**: Admin, Manager, Cashier, Inventory Manager roles
- **User Profiles**: Staff management with photos and details
- **Authentication**: Secure login/logout system
- **Permission System**: Different access levels for different user roles

### 📊 **Reporting & Analytics**
- **Dashboard**: Overview of key metrics and alerts
- **Sales Reports**: Daily, monthly, and custom date range reports
- **Stock Reports**: Inventory valuation and stock movement reports
- **Low Stock Alerts**: Automatic notifications for low inventory
- **Cashier Reports**: Individual staff performance tracking

### ⚙️ **Customization & Configuration**
- **Company Settings**: Easily customize company name, logo, colors
- **Tax Configuration**: Configurable tax rates
- **Currency Settings**: Customizable currency symbols
- **Receipt Customization**: Custom footer text for receipts
- **Theme Colors**: Customizable primary and secondary colors

## Technology Stack

- **Backend**: Django 5.2.6 (Python)
- **Frontend**: Tailwind CSS (via CDN)
- **Database**: SQLite (default, easily changeable to PostgreSQL/MySQL)
- **Authentication**: Django built-in authentication system
- **Icons**: Font Awesome 6
- **Image Processing**: Pillow for product images

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Quick Start

1. **Clone or Download the Project**
   ```bash
   cd INVENTORY_POS_APP
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv env
   
   # On Windows
   env\Scripts\activate
   
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install django pillow python-decouple
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   COMPANY_NAME=Your Company Name
   PRIMARY_COLOR=blue
   SECONDARY_COLOR=gray
   ```

5. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - Main Application: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Default Login

After creating a superuser, you can log in with those credentials. The system will automatically create a user profile with admin permissions.

## Project Structure

```
INVENTORY_POS_APP/
├── inventory_pos/          # Main project settings
├── inventory/              # Inventory management app
├── pos/                    # Point of sale app
├── accounts/               # User management app
├── templates/              # HTML templates
│   ├── base/              # Base templates
│   ├── inventory/         # Inventory templates
│   ├── pos/               # POS templates
│   └── accounts/          # Account templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User uploaded files
├── env/                   # Virtual environment
└── manage.py              # Django management script
```

## Key Models

### Inventory App
- **Category**: Product categories
- **Supplier**: Supplier information
- **Product**: Main product model with pricing and stock
- **Customer**: Customer information
- **StockMovement**: Track all stock changes

### POS App
- **Sale**: Sales transactions
- **SaleItem**: Individual items in a sale
- **Cart**: Temporary shopping cart
- **PaymentRecord**: Payment tracking
- **Refund**: Return/refund management

### Accounts App
- **UserProfile**: Extended user information
- **CompanySettings**: Customizable company settings

## Customization for Clients

This system is designed to be easily customizable for different clients:

### 1. **Company Branding**
- Update company name, logo, and colors in the admin panel
- Customize receipt templates
- Modify color themes

### 2. **Business Logic**
- Add custom fields to models
- Modify pricing structures
- Add custom reports
- Integrate with external systems

### 3. **UI/UX Customization**
- Modify templates for client-specific layouts
- Add custom CSS for unique styling
- Customize navigation and workflow

### 4. **Feature Extensions**
- Add loyalty programs
- Integrate with accounting software
- Add advanced reporting
- Implement multi-location support

## Admin Panel Features

Access the admin panel at `/admin/` to:

- Manage all products, categories, and suppliers
- View and process sales transactions
- Manage user accounts and permissions
- Configure company settings
- Generate reports and analytics
- Handle refunds and returns

## API Endpoints

The system includes AJAX endpoints for:
- Product search in POS
- Customer search
- Cart management
- Real-time updates

## Security Features

- Role-based access control
- CSRF protection
- SQL injection protection (Django ORM)
- XSS protection
- Secure password handling
- Session management

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in environment variables
2. Configure a production database (PostgreSQL recommended)
3. Set up proper static file serving
4. Use a production WSGI server (Gunicorn, uWSGI)
5. Configure HTTPS
6. Set up proper backup procedures

## Support & Customization

This application is designed to be a foundation that can be customized for specific client needs. Common customizations include:

- Custom reporting requirements
- Integration with existing systems
- Specific workflow modifications
- Additional features and modules
- Custom branding and themes

## License

This project is created as a customizable base for client projects. Modify and adapt as needed for your specific requirements.

## Contributing

This is a base template for client projects. Feel free to extend and modify according to your business needs.

---

**Built with ❤️ using Django and Tailwind CSS**
