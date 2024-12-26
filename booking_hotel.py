import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from ttkthemes import ThemedTk

# Base Room Class
class Room:
    def __init__(self, room_number, price, amenities=None, max_occupancy=2, 
                 is_available=True, checkin_time=None, nights=0, guest_name=""):
        self.room_number = room_number
        self.price = price
        self.amenities = amenities or []
        self.max_occupancy = max_occupancy
        self.is_available = is_available
        self.checkin_time = datetime.strptime(checkin_time, '%Y-%m-%d %H:%M:%S') if checkin_time else None
        self.nights = nights
        self.guest_name = guest_name

    def book_room(self, nights, guest_name):
        if self.is_available:
            self.is_available = False
            self.checkin_time = datetime.now()
            self.nights = nights
            self.guest_name = guest_name
            return True
        return False

    def release_room(self):
        self.is_available = True
        self.checkin_time = None
        self.nights = 0
        self.guest_name = ""
        
    def calculate_price(self):
        """Base price calculation method"""
        return self.price * self.nights

    def to_dict(self):
        return {
            'room_number': self.room_number,
            'room_type': self.__class__.__name__,
            'price': self.price,
            'amenities': self.amenities,
            'max_occupancy': self.max_occupancy,
            'is_available': self.is_available,
            'checkin_time': self.checkin_time.strftime('%Y-%m-%d %H:%M:%S') if self.checkin_time else None,
            'nights': self.nights,
            'guest_name': self.guest_name
        }

    @staticmethod
    def from_dict(data):
        room_types = {
            'StandardRoom': StandardRoom,
            'DeluxeRoom': DeluxeRoom,
            'SuiteRoom': SuiteRoom
        }
        room_class = room_types.get(data['room_type'], Room)
        return room_class(
            room_number=data['room_number'],
            price=data['price'],
            amenities=data.get('amenities', []),
            max_occupancy=data.get('max_occupancy', 2),
            is_available=data['is_available'],
            checkin_time=data['checkin_time'],
            nights=data['nights']
        )

# Inherited Room Classes
class StandardRoom(Room):
    def __init__(self, room_number, price, **kwargs):
        super().__init__(room_number, price, **kwargs)
        self.amenities.extend(['TV', 'AC', 'WiFi'])
        self.room_type = "Standard"
        self.max_occupancy = 2

    def calculate_price(self):
        """Override price calculation for standard room"""
        base_price = super().calculate_price()
        # No additional charges for standard room
        return base_price

class DeluxeRoom(Room):
    def __init__(self, room_number, price, **kwargs):
        super().__init__(room_number, price, **kwargs)
        self.amenities.extend(['TV', 'AC', 'WiFi', 'Mini Bar', 'City View'])
        self.room_type = "Deluxe"
        self.max_occupancy = 3

    def calculate_price(self):
        """Override price calculation for deluxe room"""
        base_price = super().calculate_price()
        # Add 10% service charge for deluxe rooms
        service_charge = base_price * 0.10
        return base_price + service_charge

class SuiteRoom(Room):
    def __init__(self, room_number, price, **kwargs):
        super().__init__(room_number, price, **kwargs)
        self.amenities.extend(['TV', 'AC', 'WiFi', 'Mini Bar', 'City View', 
                             'Living Room', 'Kitchen', 'Jacuzzi'])
        self.room_type = "Suite"
        self.max_occupancy = 4
        
    def book_room(self, nights, guest_name):
        """Override booking method for suite rooms"""
        if super().book_room(nights, guest_name):
            # Additional VIP treatment for suite rooms
            self.arrange_vip_welcome()
            return True
        return False
    
    def arrange_vip_welcome(self):
        """Special method for suite rooms"""
        self.amenities.append('Welcome Champagne')
        self.amenities.append('Fruit Basket')

    def calculate_price(self):
        """Override price calculation for suite room"""
        base_price = super().calculate_price()
        # Add 15% service charge and additional amenities fee
        service_charge = base_price * 0.15
        amenities_fee = 500000  # Fixed fee for extra amenities
        return base_price + service_charge + amenities_fee

# Modified Admin class to handle room types
class Admin:
    def __init__(self):
        self.rooms = []

    def add_room(self, room_type, room_number, price, **kwargs):
        room_classes = {
            'Standard': StandardRoom,
            'Deluxe': DeluxeRoom,
            'Suite': SuiteRoom
        }
        
        room_class = room_classes.get(room_type)
        if room_class:
            room = room_class(room_number, price, **kwargs)
            self.rooms.append(room)
            return True
        return False

    def remove_room(self, room_number):
        self.rooms = [room for room in self.rooms if room.room_number != room_number]

    def get_room_by_number(self, room_number):
        for room in self.rooms:
            if int(room.room_number) == int(room_number):
                return room
        return None

    def get_booking_statistics(self):
        total_rooms = len(self.rooms)
        occupied_rooms = len([room for room in self.rooms if not room.is_available])
        total_revenue = sum([room.price * room.nights for room in self.rooms if not room.is_available])
        return {
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'available_rooms': total_rooms - occupied_rooms,
            'occupancy_rate': (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0,
            'total_revenue': total_revenue
        }

    def to_dict(self):
        return [room.to_dict() for room in self.rooms]

    @staticmethod
    def from_dict(data):
        admin = Admin()
        admin.rooms = [Room.from_dict(room) for room in data]
        return admin

class ModernHotelBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel CG - Booking System")
        self.root.geometry("1024x768")
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'primary': '#2C3E50',
            'secondary': '#34495E',
            'accent': '#3498DB',
            'success': '#2ECC71',
            'warning': '#F1C40F',
            'danger': '#E74C3C',
            'light': '#ECF0F1',
            'dark': '#2C3E50'
        }
        
        # Configure styles
        self.style.configure('Primary.TButton',
                   background=self.colors['primary'],
                   foreground='white',
                   padding=10,
                   font=('Helvetica', 10))
        self.style.map('Primary.TButton',
                   background=[('active', self.colors['accent'])],
                   foreground=[('active', 'white')])
        
        # Admin instance
        self.admin = self.load_rooms_from_json()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Content area
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Start with main menu
        self.show_main_menu()
        
        # Handle close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    def create_header(self):
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame,
                              text="Hotel CG",
                              font=('Helvetica', 24, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Add navigation buttons
        nav_frame = ttk.Frame(header_frame)
        nav_frame.pack(side=tk.RIGHT)
        
        ttk.Button(nav_frame,
                  text="Home",
                  style='Primary.TButton',
                  command=self.show_main_menu).pack(side=tk.LEFT, padx=5)

    def show_main_menu(self):
        self.clear_content()
        
        menu_frame = ttk.Frame(self.content_frame)
        menu_frame.pack(expand=True)
        
        # Welcome message
        ttk.Label(menu_frame,
            text="Selamat Datang di Hotel CG",
            font=('Helvetica', 20, 'bold')).pack(pady=20)
        
        # Menu buttons
        buttons_frame = ttk.Frame(menu_frame)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame,
            text="Panel Admin",
            style='Primary.TButton',
            command=self.show_admin_panel).pack(pady=10)
        
        ttk.Button(buttons_frame,
            text="Panel Pelanggan",
            style='Primary.TButton',
            command=self.show_customer_panel).pack(pady=10)
        
        ttk.Button(buttons_frame,
            text="Customer Checkout",
            style='Primary.TButton',
            command=self.show_customer_checkout).pack(pady=10)

    def show_admin_panel(self):
        self.clear_content()
        
        admin_frame = ttk.Frame(self.content_frame)
        admin_frame.pack(fill=tk.BOTH, expand=True)
        
        # Statistics section
        self.show_statistics(admin_frame)
        
        # Room management section
        self.show_room_management(admin_frame)

    def show_statistics(self, parent_frame):
        stats_frame = ttk.LabelFrame(parent_frame, text="Statistik Hotel")
        stats_frame.pack(fill=tk.X, pady=10, padx=5)
        
        stats = self.admin.get_booking_statistics()
        
        # Create grid of statistics
        labels = [
            f"Jumlah Kamar: {stats['total_rooms']}",
            f"Kamar Terpakai: {stats['occupied_rooms']}",
            f"Kamar Tersedia: {stats['available_rooms']}",
            f"Tingkat Hunian: {stats['occupancy_rate']:.1f}%",
            f"Total Revenue: Rp{stats['total_revenue']:,.2f}"
        ]
        
        for i, text in enumerate(labels):
            ttk.Label(stats_frame,
                     text=text,
                     font=('Helvetica', 10)).grid(row=i//3,
                                                column=i%3,
                                                padx=10,
                                                pady=5)
    def show_customer_checkout(self):
        self.clear_content()
        
        checkout_frame = ttk.Frame(self.content_frame)
        checkout_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for occupied rooms
        columns = ('Nomor Kamar', 'Jenis', 'Tamu', 'Check-in', 'Malam', 'Total Biaya')
        tree = ttk.Treeview(checkout_frame, columns=columns, show='headings')
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add data for occupied rooms only
        for room in self.admin.rooms:
            if not room.is_available:
                total_cost = room.calculate_price()
                checkin = room.checkin_time.strftime('%Y-%m-%d %H:%M') if room.checkin_time else "-"
                tree.insert('', tk.END, values=(
                    room.room_number,
                    room.room_type,
                    room.guest_name,
                    checkin,
                    room.nights,
                    f"Rp{total_cost:,.2f}"
                ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(checkout_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack everything
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def process_checkout():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Pilih kamar untuk checkout")
                return
                
            room_number = tree.item(selected_item)['values'][0]
            room = self.admin.get_room_by_number(room_number)
            print(room)
            if room:
                # Calculate final bill
                total_cost = room.calculate_price()
                checkout_time = datetime.now()
                duration = checkout_time - room.checkin_time
                
                # Show confirmation dialog with bill details
                confirm = messagebox.askyesno(
                    "Konfirmasi Checkout",
                    f"Detail Checkout:\n\n"
                    f"Kamar: {room.room_number} ({room.room_type})\n"
                    f"Tamu: {room.guest_name}\n"
                    f"Check-in: {room.checkin_time.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Check-out: {checkout_time.strftime('%Y-%m-%d %H:%M')}\n"
                    f"Durasi: {room.nights} malam\n"
                    f"Total Biaya: Rp{total_cost:,.2f}\n\n"
                    "Lanjutkan checkout?"
                )
                
                if confirm:
                    # Generate checkout receipt
                    self.generate_checkout_receipt(room, checkout_time, total_cost)
                    
                    # Release the room
                    room.release_room()
                    
                    # Remove from treeview
                    tree.delete(selected_item)
                    
                    messagebox.showinfo("Success", "Checkout berhasil!")
        
        # Add checkout button
        ttk.Button(self.content_frame,
                text="Process Checkout",
                style='Primary.TButton',
                command=process_checkout).pack(pady=10)
        
        # Back button
        ttk.Button(self.content_frame,
                text="Kembali",
                style='Primary.TButton',
                command=self.show_main_menu).pack(pady=10)

    def generate_checkout_receipt(self, room, checkout_time, total_cost):
        if not os.path.exists('receipts'):
            os.makedirs('receipts')
            
        filename = f"receipts/Hotel_CG_Checkout_{room.room_number}_{checkout_time.strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        ))
        
        elements = []
        
        # Header
        elements.append(Paragraph("Hotel CG", styles['CustomTitle']))
        elements.append(Paragraph("Checkout Receipt", styles['Heading2']))
        elements.append(Spacer(1, 20))
        
        # Receipt details
        receipt_data = [
            ['Receipt Number:', f'RCP-{room.room_number}-{checkout_time.strftime("%Y%m%d%H%M")}'],
            ['Checkout Date:', checkout_time.strftime('%Y-%m-%d %H:%M')],
            ['Room Number:', room.room_number],
            ['Room Type:', room.room_type],
            ['Guest Name:', room.guest_name],
            ['Check-in:', room.checkin_time.strftime('%Y-%m-%d %H:%M')],
            ['Check-out:', checkout_time.strftime('%Y-%m-%d %H:%M')],
            ['Duration:', f'{room.nights} nights'],
            ['Base Rate:', f'Rp{room.price:,.2f} per night'],
        ]
        
        t = Table(receipt_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # Charges breakdown
        base_price = room.price * room.nights
        additional_charges = total_cost - base_price
        
        charges_data = [
            ['Base Charges:', f'Rp{base_price:,.2f}'],
            ['Additional Charges:', f'Rp{additional_charges:,.2f}'],
            ['Total Amount:', f'Rp{total_cost:,.2f}']
        ]
        
        t = Table(charges_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LINEABOVE', (0,-1), (-1,-1), 1, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 1, colors.black),
        ]))
        elements.append(t)
        
        # Thank you message
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Thank you for staying at Hotel CG!", styles['Heading3']))
        elements.append(Paragraph("We hope to see you again soon.", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        messagebox.showinfo("Receipt Generated", f"Checkout receipt has been saved to {filename}")
    def show_room_management(self, parent_frame):
        room_frame = ttk.LabelFrame(parent_frame, text="Manajemen Kamar")
        room_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        
        # Add room form
        form_frame = ttk.Frame(room_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Room details entries
        details_frame = ttk.Frame(form_frame)
        details_frame.pack(side=tk.LEFT, padx=10)
        
        # Room Type Selection
        ttk.Label(details_frame, text="Jenis Kamar:").grid(row=0, column=0, padx=5, pady=2)
        self.room_type_var = tk.StringVar(value="Standard")
        room_type_combo = ttk.Combobox(details_frame, 
                                     textvariable=self.room_type_var,
                                     values=["Standard", "Deluxe", "Suite"])
        room_type_combo.grid(row=0, column=1, padx=5, pady=2)
        
        fields = [
            ('Nomor Kamar:', 'room_number'),
            ('Harga:', 'price'),
        ]
        
        self.room_entries = {}
        for i, (label, key) in enumerate(fields, start=1):
            ttk.Label(details_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
            entry = ttk.Entry(details_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.room_entries[key] = entry
        
        # Additional Amenities (optional)
        amenities_frame = ttk.Frame(form_frame)
        amenities_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(amenities_frame, text="Fasilitas Tambahan:").pack()
        self.amenities_text = tk.Text(amenities_frame, height=4, width=30)
        self.amenities_text.pack()
        ttk.Label(amenities_frame,
                 text="Masukkan fasilitas tambahan yang dipisahkan dengan koma").pack()
        
        # Buttons
        buttons_frame = ttk.Frame(room_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame,
                  text="Tambahkan Kamar",
                  style='Primary.TButton',
                  command=self.add_room).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame,
                  text="Lihat Kamar",
                  style='Primary.TButton',
                  command=self.view_rooms_admin).pack(side=tk.LEFT, padx=5)

    def add_room(self):
        try:
            room_number = self.room_entries['room_number'].get()
            price = float(self.room_entries['price'].get())
            room_type = self.room_type_var.get()
            additional_amenities = [a.strip() for a in self.amenities_text.get("1.0", tk.END).split(',') if a.strip()]
            
            if not all([room_number, price > 0, room_type]):
                raise ValueError("All fields are required and must be valid.")
            
            if self.admin.add_room(room_type, room_number, price, amenities=additional_amenities):
                messagebox.showinfo("Success", f"Kamar {room_number} ({room_type}) sukses ditambahkan!")
                
                # Clear entries
                for entry in self.room_entries.values():
                    entry.delete(0, tk.END)
                self.amenities_text.delete("1.0", tk.END)
            else:
                messagebox.showerror("Error", "Invalid room type")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))


    def view_rooms_admin(self):
        self.clear_content()
        
        rooms_frame = ttk.Frame(self.content_frame)
        rooms_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('Nomor Kamar', 'Jenis', 'Harga', 'Status', 'Tamu', 'Check-in', 'Fasilitas')
        tree = ttk.Treeview(rooms_frame, columns=columns, show='headings')
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Adjust facilities column width
        tree.column('Fasilitas', width=200)
        
        # Add data
        for room in self.admin.rooms:
            status = "Available" if room.is_available else "Occupied"
            checkin = room.checkin_time.strftime('%Y-%m-%d %H:%M') if room.checkin_time else "-"
            tree.insert('', tk.END, values=(
                room.room_number,
                room.room_type,
                f"Rp{room.price:,.2f}",
                status,
                room.guest_name or "-",
                checkin,
                ', '.join(room.amenities)
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(rooms_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack everything
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Back button
        ttk.Button(self.content_frame,
                  text="Kembali",
                  style='Primary.TButton',
                  command=self.show_admin_panel).pack(pady=10)

    def show_customer_panel(self):
        self.clear_content()
        
        customer_frame = ttk.Frame(self.content_frame)
        customer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search and filter section
        filter_frame = ttk.LabelFrame(customer_frame, text="Search Rooms")
        filter_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Add filter options
        ttk.Label(filter_frame, text="Jenis Kamar:").pack(side=tk.LEFT, padx=5)
        room_types = list(set(room.room_type for room in self.admin.rooms))
        self.room_type_var = tk.StringVar(value="Semua")
        ttk.Combobox(filter_frame,
                    textvariable=self.room_type_var,
                    values=["Semua"] + room_types).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame,
                  text="Search",
                  style='Primary.TButton',
                  command=self.filter_rooms).pack(side=tk.LEFT, padx=5)
        
        # Available rooms section
    def filter_rooms(self):
        selected_type = self.room_type_var.get()
        self.show_available_rooms(selected_type)

    def show_available_rooms(self, filter_type="Semua"):
        # Clear previous room display
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                widget.destroy()
                
        rooms_frame = ttk.LabelFrame(self.content_frame, text="Kamar yang Tersedia")
        rooms_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        
        # Create canvas for scrolling
        canvas = tk.Canvas(rooms_frame)
        scrollbar = ttk.Scrollbar(rooms_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display rooms
        for room in self.admin.rooms:
            if not room.is_available:
                continue
            if filter_type != "Semua" and room.room_type != filter_type:
                continue
                
            room_card = ttk.LabelFrame(scrollable_frame, text=f"Kamar {room.room_number}")
            room_card.pack(fill=tk.X, padx=5, pady=5)
            
            # Room details
            details_frame = ttk.Frame(room_card)
            details_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(details_frame,
                     text=f"Jenis: {room.room_type}",
                     font=('Helvetica', 10, 'bold')).pack(anchor="w")
            
            ttk.Label(details_frame,
                     text=f"Harga: Rp{room.price:,.2f} per night",
                     font=('Helvetica', 10)).pack(anchor="w")
            
            ttk.Label(details_frame,
                     text=f"Maksimal Orang: {room.max_occupancy} Orang",
                     font=('Helvetica', 10)).pack(anchor="w")
            
            # Amenities
            if room.amenities:
                ttk.Label(details_frame,
                         text="Fasilitas: " + ", ".join(room.amenities),
                         font=('Helvetica', 10)).pack(anchor="w")
            
            # Book button
            ttk.Button(details_frame,
                      text="Booking Sekarang",
                      style='Primary.TButton',
                      command=lambda r=room: self.show_booking_form(r)).pack(pady=10)
        
        # Pack scrollbar and canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_booking_form(self, room):
        booking_window = tk.Toplevel(self.root)
        booking_window.title(f"Booking {room.room_type} Room {room.room_number}")
        booking_window.geometry("500x700")
        
        form_frame = ttk.Frame(booking_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Room details
        ttk.Label(form_frame,
                 text=f"Booking Details - {room.room_type} Room {room.room_number}",
                 font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        details_text = f"""
Type: {room.room_type} Room
Price per night: Rp{room.price:,.2f}
Maximum Occupancy: {room.max_occupancy} Persons
Amenities: {', '.join(room.amenities)}
"""
        ttk.Label(form_frame,
                 text=details_text,
                 justify=tk.LEFT).pack(pady=10)
        
        # Guest details form
        guest_frame = ttk.LabelFrame(form_frame, text="Guest Information")
        guest_frame.pack(fill=tk.X, pady=10)
        
        fields = [
            ('Full Name:', 'name'),
            ('Email:', 'email'),
            ('Phone:', 'phone'),
            ('Number of Nights:', 'nights')
        ]
        
        entries = {}
        for label, key in fields:
            frame = ttk.Frame(guest_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=5)
            entry = ttk.Entry(frame)
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
            entries[key] = entry
        
        # Special requests
        ttk.Label(guest_frame, text="Special Requests:").pack(anchor="w", padx=5)
        requests_text = tk.Text(guest_frame, height=4)
        requests_text.pack(fill=tk.X, padx=5, pady=5)
        
        def confirm_booking():
            try:
                guest_name = entries['name'].get().strip()
                email = entries['email'].get().strip()
                phone = entries['phone'].get().strip()
                nights = int(entries['nights'].get())
                special_requests = requests_text.get("1.0", tk.END).strip()
                
                if not all([guest_name, email, phone, nights > 0]):
                    raise ValueError("Please fill in all required fields.")
                
                if room.book_room(nights, guest_name):
                    self.generate_modern_invoice(room, {
                        'guest_name': guest_name,
                        'email': email,
                        'phone': phone,
                        'special_requests': special_requests
                    })
                    
                    booking_window.destroy()
                    self.show_customer_panel()
                else:
                    messagebox.showerror("Error", "Room is no longer available.")
                    
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(form_frame,
                  text="Confirm Booking",
                  style='Primary.TButton',
                  command=confirm_booking).pack(pady=20)


    def generate_modern_invoice(self, room, guest_details):
        if not os.path.exists('invoices'):
            os.makedirs('invoices')
            
        filename = f"invoices/Hotel_CG_Invoice_{room.room_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        ))
        
        elements = []
        
        # Header
        elements.append(Paragraph("Hotel CG", styles['CustomTitle']))
        elements.append(Paragraph(f"{room.room_type} Room Invoice", styles['Heading2']))
        elements.append(Spacer(1, 20))
        
        # Invoice details
        invoice_data = [
            ['Tanggal Faktur:', datetime.now().strftime('%Y-%m-%d %H:%M')],
            ['Nomor Faktur:', f'INV-{room.room_number}-{datetime.now().strftime("%Y%m%d%H%M")}'],
            ['Nomor Kamar:', room.room_number],
            ['Jenis Kamar:', room.room_type],
            ['Fasilitas:', ', '.join(room.amenities)]
        ]
        
        t = Table(invoice_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # Pricing details
        base_price = room.price * room.nights
        total_price = room.calculate_price()
        additional_charges = total_price - base_price
        
        pricing_data = [
            ['Base Price:', f'Rp{base_price:,.2f}'],
            ['Additional Charges:', f'Rp{additional_charges:,.2f}'],
            ['Total Price:', f'Rp{total_price:,.2f}']
        ]
        
        t = Table(pricing_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        elements.append(t)
        
        # Build PDF
        doc.build(elements)
        messagebox.showinfo("Faktur Generated", f"Faktur telah disimpan di {filename}")

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def load_rooms_from_json(self):
        try:
            with open("rooms.json", "r") as file:
                data = json.load(file)
                return Admin.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return Admin()

    def save_rooms_to_json(self):
        with open("rooms.json", "w") as file:
            json.dump(self.admin.to_dict(), file, indent=4)

    def on_close(self):
        self.save_rooms_to_json()
        self.root.destroy()

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  
    app = ModernHotelBookingApp(root)
    root.mainloop()