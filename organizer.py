import tkinter as tk
import sqlalchemy
import org_db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class OrganizerApp:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        #create main container
        self.root = tk.Tk()
        self.root.title("Organizer v0.1")
        self.root.geometry("{}x{}".format(self.width, self.height))
        self.root.resizable(False, False)
        
        #create main frame which include all records
        self.main_frame = tk.Frame(self.root, width=300, height=250)
        self.main_frame.pack()    
        
        #create frame for menu buttons
        self.opt_frame = tk.Frame(self.root, width=300, height=80)
        self.opt_frame.pack(side='bottom', pady=20)
        
        self.opt_frame.grid_columnconfigure(0, weight=2)
        
        self.button_view = tk.Button(self.opt_frame)
        self.button_view.config(font="Arial 12", text="View")
        self.button_view.grid(row=0, column=0, sticky='we')
        self.active_button_settings(
                        self.button_view, 
                        lambda event: self.get_records("category")
                        )
        
        self.button_create = tk.Button(self.opt_frame, text="Create")
        self.button_create.grid(row=0, column=1, sticky='we')
        self.active_button_settings(
                        self.button_create, 
                        lambda event: self.create_new_record("category")
                        )
        
        #bind app with db
        self.engine = create_engine("sqlite:///org.db")
        self.Session = sessionmaker(bind=self.engine)
        
        #show all categories
        self.get_records("category")
        
        self.root.mainloop()
        
    def active_button_settings(self, widget, func):
        '''
        Function bind button with func, 
        and set config for active button.
        '''
        widget.bind("<Button-1>", func)
        widget.config(
                font="Arial 12", 
                fg="black", 
                bg="#228B22", 
                activebackground="#32CD32", 
                activeforeground="white",  
                cursor="hand1", 
                width=14
                )
    
    def unactive_button_settings(self, widget):
        '''
        Function for unbind button and set button as unactive. 
        '''
        widget.unbind("<Button-1>")
        widget.configure(
                bg="gray", 
                activebackground="gray", 
                activeforeground="black", 
                cursor="arrow"
                )
    
        
    def clear_main_frame(self):
        '''
        Function for clear main_frame.
        '''
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def create_new_record(self, table_name, cat_id=None):
        '''
        Function for displaing window for add new record.
        '''
        self.clear_main_frame()
        if table_name == "category":
            text = "Enter name the new category:"
            self.active_button_settings(
                            self.button_view, 
                            lambda event: self.get_records("category")
                            )
        else:
            text = "Enter text new record:"
            self.active_button_settings(
                            self.button_view, 
                            lambda event: self.get_records(
                                                    "record", cat_id
                                                    )
                            )
            
        lb = tk.Label(self.main_frame, text=text, font="Arial 16")
        lb.pack(fill='x', pady=10)
        
        e = tk.Entry(self.main_frame, font="Arial 16")
        e.pack(fill='x', pady=10)
        
        b = tk.Button(
                self.main_frame, 
                font="Arial 16", 
                text="Add", 
                width=20, 
                pady=10,
                fg="black", 
                activebackground="#32CD32", 
                activeforeground="white",  
                cursor="hand1"
                )
        b.pack(fill='x', pady=10)
        b.bind(
            "<Button-1>", 
            lambda event: self.save_new_record_db(e, cat_id)
            )
            
        
        self.unactive_button_settings(self.button_create)
    
    def save_new_record_db(self, entry, cat_id=None):
        '''
        Function for save new record to database.
        '''
        text = entry.get()
        if text:
            #entry text must include characters except space
            new_text = text.replace(' ', '')
            if new_text:
                session = self.Session()
                if cat_id:
                    rec = org_db.Record(category_id=cat_id, text=text)
                else:
                    rec = org_db.Category(name=text)
                session.add(rec)
                session.commit()
                if cat_id:
                    self.get_records("record", cat_id)
                else:
                    self.get_records("category")
            
        
    def display_rows(self, table_name, container):
        '''
        Function display all records from 'container' 
        depending on 'table_name'.
        '''
        # scroll bar
        self.scrollbar_vert = tk.Scrollbar(
                                    self.main_frame, orient="vertical"
                                    )
        self.scrollbar_vert.pack(side = 'right', fill = 'y')

        #canvas
        self.canvas = tk.Canvas(
                        self.main_frame, 
                        borderwidth=0,  
                        bg = 'white'
                        )
        self.inner_frame = tk.Frame(self.canvas,  bg = 'white')
            
        #command for scrolling
        self.scrollbar_vert["command"] = self.canvas.yview
            
        #canvas settings
        self.canvas.configure(
                        yscrollcommand=self.scrollbar_vert.set, 
                        width=self.width - 50, 
                        heigh=self.height - 70
                        ) 
            
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.create_window(
                                (0,0), 
                                window=self.inner_frame, 
                                anchor="nw"
                                )
        
        #fill out the records with the frame
        for i in range(1, len(container)+1):
            if(table_name == "category"):
                text = container[i-1].name
                main_widget = tk.Button
            else:
                text = container[i-1].text
                main_widget = tk.Checkbutton
                    
            
            #settings for container    elements
            isv = tk.StringVar()
            isv.set("{}. {}".format(i, text))
            
            if table_name == "record":
                #settings checkbutton for records
                check_status = tk.IntVar()
                check_status.set(int(container[i-1].status))
                cb = main_widget(
                            self.inner_frame, variable=check_status
                            )
                cb.bind(
                    "<Button-1>", 
                    lambda event, check_status=check_status, i=i:\
                    self.check_event(check_status, container[i-1].id)
                    )
            else:
                cb = main_widget(self.inner_frame)
            cb.config(
                    textvariable=isv, 
                    anchor="w", 
                    bg="white", 
                    font="Arial 16", 
                    wraplength=237
                    )
            
            cb.grid(row=i, column=0, pady=2)
            
            #delete button
            lb = tk.Button(
                        self.inner_frame, 
                        text="x", 
                        padx=10, 
                        bg="#B22222", 
                        activebackground="red",
                        activeforeground="white",
                        fg="white", 
                        font="Arial 14", 
                        borderwidth=1, 
                        relief="groove",
                        cursor="hand1"
                        )
            lb.grid(row=i, column=1, sticky="nsew", pady=2)
            lb.bind(
                    '<Button-1>', 
                    lambda event, i=i: \
                    self.delete_record_from_db(
                                        table_name, container[i-1].id
                                        )
                    )
                
            if(table_name == "category"):
                cb.config(width=20)
                cb.bind(
                    "<Button-1>", 
                    lambda event, i=i: \
                    self.get_records("record", cat_id=container[i-1].id)
                    )
            else:
                lb.config(padx=5)
                cb.config(width=20, font="Arial 16", pady=5)
                
            cb.bind(
                '<4>', 
                lambda event : self.canvas.yview('scroll', -1, 'units')
                )
            cb.bind(
                '<5>', 
                lambda event : self.canvas.yview('scroll', 1, 'units')
                )
                
            lb.bind(
                '<4>', 
                lambda event : self.canvas.yview('scroll', -1, 'units')
                )
            lb.bind(
                '<5>', 
                lambda event : self.canvas.yview('scroll', 1, 'units')
                )
                
        #update inner_frame and set scrolling
        self.inner_frame.update()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        self.inner_frame.bind(
                '<4>', 
                lambda event : self.canvas.yview('scroll', -1, 'units')
                )
        self.inner_frame.bind(
                '<5>', 
                lambda event : self.canvas.yview('scroll', 1, 'units')
                )
                
            
        self.canvas.bind(
                '<4>', 
                lambda event : self.canvas.yview('scroll', -1, 'units')
                )
        self.canvas.bind(
                '<5>', 
                lambda event : self.canvas.yview('scroll', 1, 'units')
                )
    
    def check_event(self, check_status, rec_id):
        '''
        Function for change status of record.
        '''
        session = self.Session()
        rec = session.query(org_db.Record).get(rec_id)
        if check_status.get() == 0:
            rec.status = True
        else:
            rec.status = False
        session.commit()
        
    
    
    def get_records(self, table_name, cat_id=None):
        '''
        Function get records from db.
        '''
        session = self.Session()
        self.clear_main_frame()
        if table_name == "category":
            records = list(session.query(org_db.Category).all())
            if records:
                self.display_rows("category", records)
            else:
                self.default_message("Not yet categories.")
            self.unactive_button_settings(self.button_view)
            self.active_button_settings(
                        self.button_create, 
                        lambda event: self.create_new_record("category")
                        )
                
        else:
            records = list(
                        session.query(org_db.Record).filter_by(
                                                category_id=cat_id
                                                )
                        )
            if records:
                self.display_rows("record", records)
            else:    
                self.default_message("Not yet records.")
            self.active_button_settings(
                            self.button_view, 
                            lambda event: self.get_records("category")
                            )
            self.active_button_settings(
                            self.button_create,  
                            lambda event: self.create_new_record(
                                                    "record", cat_id
                                                    )
                            )

    
        
    def delete_record_from_db(self, table_name, rec_id):
        '''
        Function delete category or record from database.
        '''
        #delete row from db
        session = self.Session()
        if table_name == "category":
            delete_rec = session.query(org_db.Category).get(rec_id)
        else:
            delete_rec = session.query(org_db.Record).get(rec_id)
            cat_id = delete_rec.category_id
        session.delete(delete_rec)
        session.commit()
        #show result
        if table_name == "category":
            self.get_records("category")
        else:
            self.get_records("record", cat_id)

            
        
    def default_message(self, default_text):
        '''
        Function for displaing default message, 
        if not exist categories/records
        '''
        lb = tk.Label(self.main_frame)
        lb.configure(
                font="Arial 16", 
                text=default_text, 
                bg="white", 
                padx=self.width - 270, 
                pady=self.height - 225
                )
        lb.pack()
        
        
#create app    
app = OrganizerApp(350, 350)
