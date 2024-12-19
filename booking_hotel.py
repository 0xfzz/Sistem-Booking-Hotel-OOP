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

class Room:
    def __init__(self, room_number, room_type, price, amenities=None, max_occupancy=2, 
                 is_available=True, checkin_time=None, nights=0, guest_name=""):
        self.room_number = room_number
        self.room_type = room_type
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

    def to_dict(self):
        return {
            'room_number': self.room_number,
            'room_type': self.room_type,
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
        room = Room(
            room_number=data['room_number'],
            room_type=data['room_type'],
            price=data['price'],
            amenities=data.get('amenities', []),
            max_occupancy=data.get('max_occupancy', 2),
            is_available=data['is_available'],
            checkin_time=data['checkin_time'],
            nights=data['nights']
        )
        room.guest_name = data.get('guest_name', '')
        return room

class Admin:
    def __init__(self):
        self.rooms = []

    def add_room(self, room):
        self.rooms.append(room)

    def remove_room(self, room_number):
        self.rooms = [room for room in self.rooms if room.room_number != room_number]

    def get_room_by_number(self, room_number):
        for room in self.rooms:
            if room.room_number == room_number:
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

    def show_room_management(self, parent_frame):
        room_frame = ttk.LabelFrame(parent_frame, text="Manajemen Kamar")
        room_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=5)
        
        # Add room form
        form_frame = ttk.Frame(room_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Room details entries
        details_frame = ttk.Frame(form_frame)
        details_frame.pack(side=tk.LEFT, padx=10)
        
        fields = [
            ('Nomor Kamar:', 'room_number'),
            ('Jenis Kamar:', 'room_type'),
            ('Harga:', 'price'),
            ('Maksimal Orang:', 'max_occupancy')
        ]
        
        self.room_entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(details_frame, text=label).grid(row=i, column=0, padx=5, pady=2)
            entry = ttk.Entry(details_frame)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.room_entries[key] = entry
        
        # Amenities
        amenities_frame = ttk.Frame(form_frame)
        amenities_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(amenities_frame, text="Fasilitas:").pack()
        self.amenities_text = tk.Text(amenities_frame, height=4, width=30)
        self.amenities_text.pack()
        ttk.Label(amenities_frame,
                 text="Masukkan fasilitas yang dipisahkan dengan koma").pack()
        
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
            room_type = self.room_entries['room_type'].get()
            price = float(self.room_entries['price'].get())
            max_occupancy = int(self.room_entries['max_occupancy'].get())
            amenities = [a.strip() for a in self.amenities_text.get("1.0", tk.END).split(',') if a.strip()]
            
            if not all([room_number, room_type, price > 0, max_occupancy > 0]):
                raise ValueError("All fields are required and must be valid.")
            
            room = Room(room_number, room_type, price, amenities, max_occupancy)
            self.admin.add_room(room)
            
            messagebox.showinfo("Success",
                              f"Kamar {room_number} sukses ditambahkan!")
            
            # Clear entries
            for entry in self.room_entries.values():
                entry.delete(0, tk.END)
            self.amenities_text.delete("1.0", tk.END)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def view_rooms_admin(self):
        self.clear_content()
        
        rooms_frame = ttk.Frame(self.content_frame)
        rooms_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('Nomor Kamar', 'Jenis', 'Harga', 'Status', 'Tamu', 'Check-in')
        tree = ttk.Treeview(rooms_frame, columns=columns, show='headings')
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
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
                checkin
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
        booking_window.title(f"Booking Kamar {room.room_number}")
        booking_window.geometry("500x600")
        
        # Style the window
        form_frame = ttk.Frame(booking_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Room details
        ttk.Label(form_frame,
                 text=f"Detail Booking - Kkamar {room.room_number}",
                 font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        details_text = f"""
Jenis Kamar: {room.room_type}
Harga per malam: Rp{room.price:,.2f}
Maksimal Orang: {room.max_occupancy} Orang
Fasilitas: {', '.join(room.amenities)}
        """
        ttk.Label(form_frame,
                 text=details_text,
                 justify=tk.LEFT).pack(pady=10)
        
        # Guest details
        guest_frame = ttk.LabelFrame(form_frame, text="Informasi Tamu")
        guest_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(guest_frame, text="Nama Lengkap:").pack(anchor="w", padx=5)
        name_entry = ttk.Entry(guest_frame)
        name_entry.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(guest_frame, text="Email:").pack(anchor="w", padx=5)
        email_entry = ttk.Entry(guest_frame)
        email_entry.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(guest_frame, text="No HP:").pack(anchor="w", padx=5)
        phone_entry = ttk.Entry(guest_frame)
        phone_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Booking details
        booking_details_frame = ttk.LabelFrame(form_frame, text="Detail Booking")
        booking_details_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(booking_details_frame, text="Jumlah Malam:").pack(anchor="w", padx=5)
        nights_entry = ttk.Entry(booking_details_frame)
        nights_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Special requests
        ttk.Label(booking_details_frame, text="Requests Tambahan:").pack(anchor="w", padx=5)
        requests_text = tk.Text(booking_details_frame, height=4)
        requests_text.pack(fill=tk.X, padx=5, pady=5)
        
        def confirm_booking():
            try:
                guest_name = name_entry.get().strip()
                email = email_entry.get().strip()
                phone = phone_entry.get().strip()
                nights = int(nights_entry.get())
                special_requests = requests_text.get("1.0", tk.END).strip()
                
                if not all([guest_name, email, phone, nights > 0]):
                    raise ValueError("Please fill in all required fields.")
                
                if room.book_room(nights, guest_name):
                    # Generate and save invoice
                    self.generate_modern_invoice(room, {
                        'guest_name': guest_name,
                        'email': email,
                        'phone': phone,
                        'special_requests': special_requests
                    })
                    
                    messagebox.showinfo("Success",
                                      f"Kamar {room.room_number} sukses dibooking untuk {nights} malam!")
                    booking_window.destroy()
                    self.show_customer_panel()
                else:
                    messagebox.showerror("Error", "Kamar sudah tidak tersedia.")
                    
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        # Confirm button
        ttk.Button(form_frame,
                  text="Konfirmasi Booking",
                  style='Primary.TButton',
                  command=confirm_booking).pack(pady=20)

    def generate_modern_invoice(self, room, guest_details):
        # Create directory for invoices if it doesn't exist
        if not os.path.exists('invoices'):
            os.makedirs('invoices')
            
        filename = f"invoices/Hotel_CG_Invoice_{room.room_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        
        # Styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        ))
        styles.add(ParagraphStyle(
            name='SubTitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20
        ))
        
        # Content elements
        elements = []
        
        # Logo and header
        elements.append(Paragraph("Hotel CG", styles['CustomTitle']))
        elements.append(Paragraph("Luxury Accommodation", styles['SubTitle']))
        elements.append(Spacer(1, 20))
        
        # Invoice details
        invoice_data = [
            ['Tanggal Faktur:', datetime.now().strftime('%Y-%m-%d %H:%M')],
            ['Nomor Faktur:', f'INV-{room.room_number}-{datetime.now().strftime("%Y%m%d%H%M")}'],
            ['Nomor Kamar:', room.room_number],
            ['Jenis Kamar:', room.room_type]
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
        
        # Guest information
        elements.append(Paragraph("Informasi Tamu", styles['Heading3']))
        guest_data = [
            ['Nama Tamu:', guest_details['guest_name']],
            ['Email:', guest_details['email']],
            ['No HP:', guest_details['phone']]
        ]
        
        t = Table(guest_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        
        # Booking details
        elements.append(Paragraph("Detail Booking", styles['Heading3']))
        booking_data = [
            ['Tanggal Check-In:', room.checkin_time.strftime('%Y-%m-%d %H:%M')],
            ['Jumlah Malam:', str(room.nights)],
            ['Harga per malam:', f'Rp{room.price:,.2f}'],
            ['Total:', f'Rp{(room.price * room.nights):,.2f}']
        ]
        
        if guest_details['special_requests']:
            booking_data.append(['Request Tambahan:', guest_details['special_requests']])
        
        t = Table(booking_data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
        ]))
        elements.append(t)
        
        # Build PDF
        doc.build(elements)
        messagebox.showinfo("Faktur Sudah dibuat",
                          f"Faktur sudah disave {filename}")

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