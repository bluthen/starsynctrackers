from Tkinter import *
import subprocess
import tkFileDialog
import tkMessageBox
import traceback
import process
import threading
import Queue
import time
import os

def process_wrapper(args, queue):
    fn = None
    try:
        fn = process.analyize(args, queue)
    except:
        queue.put({'status': 'error', 'message': traceback.format_exc()})
    queue.put({'status': 'done', 'message': fn}, True)


class Application(Frame):
    def __init__(self, args, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack()
        self.create_widgets(args)

    def process(self):
        # Validate
        args = {'arcsecs-per-pixel': 3.92, 'tracker-rate': 1.0, 'exposure-overwrite': None, 'filename': None}

        args['filename'] = self.file_chooser_value.get()
        try:
            with open(args['filename'], 'r') as f:
                pass
        except:
            print traceback.format_exc()
            tkMessageBox.showerror('Invalid filename', "Please select a valid image.")
            return

        try:
            args['arcsecs-per-pixel'] = float(self.arcsecs_per_pixel_value.get())
        except ValueError:
            tkMessageBox.showerror('Invalid "/pixel', "\"/pixel must be a number.")
            return

        try:
            args['tracker-rate'] = float(self.tracker_rate_value.get())
        except ValueError:
            tkMessageBox.showerror('Invalid SSTRate', "SSTRate must be a number.")
            return

        if self.overwrite_exposure_time_checkbutton_value.get() == 1:
            try:
                args['exposure-overwrite'] = float(self.overwrite_exposure_time_value.get())
            except ValueError:
                tkMessageBox.showerror('Invalid Exposure Overwrite', "If enabled exposure must be a number.")
                return

        # Process
        queue = Queue.Queue()
        t = threading.Thread(target=process_wrapper, args=(args, queue))
        self.process_button_value.set('Starting...')
        self.process_button['state'] = DISABLED
        self.master.after(250, self.update_status, queue)
        t.start()
        time.sleep(1)

    def show_image(self, fn):
        print "Doing show_image."
        print fn
        if os.name == 'nt':
            subprocess.Popen('explorer "%s"' % (fn.replace('/', '\\'),))
        elif os.name=='mac':
            subprocess.Popen('open "%s"' % (fn,), shell=True)
        elif os.name=='posix':
            subprocess.Popen('xdg-open "%s"' % (fn,), shell=True)

    def update_status(self, queue):
        try:
            while True:
                msg = queue.get_nowait()
                if msg['status'] == 'done':
                    self.process_button_value.set('Process')
                    self.process_button['state'] = NORMAL
                    self.show_image(msg['message'])
                    return
                elif msg['status'] == 'error':
                    tkMessageBox.showerror('Error Processing', msg['message'])
                else:
                    self.process_button_value.set(msg['message'])
        except Queue.Empty:
            self.master.after(250, self.update_status, queue)

    def select_file(self):
        file_opt = {}
        file_opt['defaultextension'] = '.jpg'
        file_opt['filetypes'] = [('all files', '.*'), ('JPEGs', '.jpg,.JPG')]
        file_opt['parent'] = self.master
        file_opt['title'] = 'Select Image to Analyze...'

        filename = tkFileDialog.askopenfilename(**file_opt)
        print self
        self.file_chooser_value.set(filename)

    def toggle_overwrite_exposure_time(self):
        if self.overwrite_exposure_time_checkbutton_value.get() == 1:
            self.overwrite_exposure_time_entry['state'] = NORMAL
        else:
            self.overwrite_exposure_time_entry['state'] = DISABLED

    def create_widgets(self, args):
        if args is None:
            args = {'arcsecs-per-pixel': 3.92, 'tracker-rate': 1.0, 'exposure-overwrite': None, 'filename': None}
        self.file_chooser_label = Label(self, text='File: ')
        self.file_chooser_label.grid({"row": 0, "column": 0})
        self.file_chooser_value = StringVar()
        if args['filename']:
            self.file_chooser_value.set(args['filename'])
        self.file_chooser = Button(self, text='(Select File)', command=self.select_file, textvariable=self.file_chooser_value)
        # self.file_chooser.pack({"side": "top"})
        self.file_chooser.grid({"row": 0, "column": 2, "columnspan": 5})

        self.arcsecs_per_pixel_label = Label(self, text='"/pixel: ')
        self.arcsecs_per_pixel_label.grid({"row": 1, "column": 0, "columnspan": 2})
        self.arcsecs_per_pixel_value = StringVar()
        if args['arcsecs-per-pixel']:
            self.arcsecs_per_pixel_value.set(str(args['arcsecs-per-pixel']))
        self.arcsecs_per_pixel_entry = Entry(self, width=5, textvariable=self.arcsecs_per_pixel_value)
        self.arcsecs_per_pixel_entry.grid({"row": 1, "column": 2})

        self.tracker_rate_label = Label(self, text='SSTRate: ')
        self.tracker_rate_label.grid({"row": 2, "column": 0, "columnspan": 2})
        self.tracker_rate_value = StringVar()
        if args['tracker-rate']:
            self.tracker_rate_value.set(str(args['tracker-rate']))
        self.tracker_rate_entry = Entry(self, width=5, textvariable=self.tracker_rate_value)
        self.tracker_rate_entry.grid({"row": 2, "column": 2})

        self.overwrite_exposure_time_checkbutton_value = IntVar()
        self.overwrite_exposure_time_value = StringVar()
        if args['exposure-overwrite']:
            self.overwrite_exposure_time_checkbutton_value.set(1)
            self.overwrite_exposure_time_value.set(str(args['exposure-overwrite']))

        self.overwrite_exposure_time_checkbutton = Checkbutton(
            self,
            command=self.toggle_overwrite_exposure_time,
            text="Overwrite Exposure Time: ",
            variable=self.overwrite_exposure_time_checkbutton_value)
        self.overwrite_exposure_time_checkbutton.grid({"row": 3, "column": 0, "columnspan": 4})

        self.overwrite_exposure_time_entry = Entry(self, width=5, textvariable=self.overwrite_exposure_time_value)
        self.overwrite_exposure_time_entry.grid({"row": 3, "column": 4})

        self.toggle_overwrite_exposure_time()

        self.process_button_value = StringVar()
        self.process_button_value.set('Process')
        self.process_button = Button(self, textvariable=self.process_button_value, command=self.process)
        self.process_button.grid({"row": 5, "column": 5})


def show(args=None):
    root = Tk()
    root.title('SST Artificial Star Error Analysis')
    app = Application(args, master=root)
    app.mainloop()


if __name__ == '__main__':
    show()
