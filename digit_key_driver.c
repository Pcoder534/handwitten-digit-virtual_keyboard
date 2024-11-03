#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/input.h>
#include <linux/mutex.h>
#include <linux/init.h>

#define DEVICE_NAME "digit_key_driver"
#define CLASS_NAME "digit_key_class"

static int major_number;
static struct class* digit_key_class = NULL;
static struct device* digit_key_device=NULL;
static struct input_dev * input_device;
static DEFINE_MUTEX(digit_key_mutex);

// Function to send the digit keypress
static int send_digit_key(int digit) {
    int keycode;
    switch(digit) {
        case 0: keycode = KEY_0; break;
        case 1: keycode = KEY_1; break;
        case 2: keycode = KEY_2; break;
        case 3: keycode = KEY_3; break;
        case 4: keycode = KEY_4; break;
        case 5: keycode = KEY_5; break;
        case 6: keycode = KEY_6; break;
        case 7: keycode = KEY_7; break;
        case 8: keycode = KEY_8; break;
        case 9: keycode = KEY_9; break;
    }

    // Report key press
    input_report_key(input_device, keycode, 1);
    input_sync(input_device);

    // Report key release
    input_report_key(input_device, keycode, 0);
    input_sync(input_device);

    printk(KERN_INFO"Simulated key press for digit %d\n", digit);
    return 0;
}
//write to file function
static ssize_t dev_write(struct file *fp, const char* buff, size_t len, loff_t* offset){
    // Lock the device
    if (!mutex_trylock(&digit_key_mutex)) {
        pr_err("Device is in use by another process\n");
        return -EBUSY;
    }
    if(len<1){
        printk(KERN_ALERT"enter a single digit(0-9)\n");
        mutex_unlock(&digit_key_mutex);
        return -1;
    }
    char digit_char;
    int r = copy_from_user(&digit_char, buff,1); //copy single digit
    int digit = digit_char -'0';
    if (digit < 0 || digit > 9) {
        printk(KERN_ERR"Invalid input. Please write a single digit (0-9).\n");
        mutex_unlock(&digit_key_mutex);
        return -1;
    }
    
    send_digit_key(digit);
    mutex_unlock(&digit_key_mutex);
    return 1;
}
static int dev_open(struct inode *inp, struct file *fp) {
    pr_info("Device opened\n");
    return 0;
}

static int dev_release(struct inode *inp, struct file *fp) {
    pr_info("Device successfully closed\n");
    return 0;
}
static struct file_operations fops = {
    .open = dev_open,
    .write = dev_write,
    .release = dev_release,
};

static int __init digit_key_init(void){
    mutex_init(&digit_key_mutex);
    
    major_number = register_chrdev(0,DEVICE_NAME,&fops);
    if(major_number<0){
        printk(KERN_ERR"error with registering device\n");
        return major_number;
    }
    printk(KERN_INFO"registered with major number: %d\n",major_number);
    
    digit_key_class = class_create(CLASS_NAME);
    if(digit_key_class==NULL){
        unregister_chrdev(major_number, DEVICE_NAME);
        printk(KERN_ERR"error in createing class\n");
        return -1;
    }
    
    digit_key_device = device_create(digit_key_class,NULL,MKDEV(major_number,0),NULL,DEVICE_NAME);
    if(digit_key_device == NULL){
        class_destroy(digit_key_class);
        unregister_chrdev(major_number, DEVICE_NAME);
    }

    // Create and register input device
    input_device = input_allocate_device();
    if (!input_device) {
        device_destroy(digit_key_class, MKDEV(major_number, 0));
        class_destroy(digit_key_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        pr_err("Failed to allocate input device\n");
        return -ENOMEM;
    }

    // Set up input device properties
    input_device->name = "Digit Key Simulator";
    input_device->phys = "digit_key/input0";
    input_device->id.bustype = BUS_VIRTUAL;
    input_device->evbit[0] = BIT_MASK(EV_KEY);

    set_bit(KEY_0, input_device->keybit);
    set_bit(KEY_1, input_device->keybit);
    set_bit(KEY_2, input_device->keybit);
    set_bit(KEY_3, input_device->keybit);
    set_bit(KEY_4, input_device->keybit);
    set_bit(KEY_5, input_device->keybit);
    set_bit(KEY_6, input_device->keybit);
    set_bit(KEY_7, input_device->keybit);
    set_bit(KEY_8, input_device->keybit);
    set_bit(KEY_9, input_device->keybit);

    int result = input_register_device(input_device);
    if (result) {
        input_free_device(input_device);
        device_destroy(digit_key_class, MKDEV(major_number, 0));
        class_destroy(digit_key_class);
        unregister_chrdev(major_number, DEVICE_NAME);
        pr_err("Failed to register input device\n");
        return result;
    }

    printk(KERN_INFO"Digit key driver loaded with device /dev/%s\n", DEVICE_NAME);
    return 0;
}
static void __exit digit_key_exit(void){
    input_free_device(input_device);
    device_destroy(digit_key_class, MKDEV(major_number, 0));
    class_destroy(digit_key_class);
    unregister_chrdev(major_number, DEVICE_NAME);
    mutex_destroy(&digit_key_mutex);
    printk(KERN_INFO"exiting the driver\n");
}

module_init(digit_key_init);
module_exit(digit_key_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("handwitten digit(0-9) virtual keyboard");
MODULE_AUTHOR("Prateek");
