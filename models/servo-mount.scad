use <MCAD/servos.scad>

servo_length = 12;
servo_width = 32;
servo_height = 31;
servo_mount_plate_height = 19;

servo_offset = (servo_width-20) / 2;

support_length = 12;
support_width = 36;
support_height = servo_height - servo_mount_plate_height;

echo("Calulated support height:", support_height);

module base_support() {
    x_offset = -support_length / 2;
    y_offset = -support_width/2 + servo_offset;
    z_offset = servo_mount_plate_height;
    
    translate([x_offset, y_offset, z_offset]) 
        cube([support_length, support_width, support_height]);
}

module spacer() {
    spacer_length = servo_length + 2;
    spacer_width = 22 + 2;
    spacer_height = support_height + 2;
    
    x_offset = -spacer_length / 2;
    y_offset = -spacer_width / 2 + servo_offset;
    z_offset = servo_mount_plate_height - 1;
    
    translate([x_offset, y_offset, z_offset]) 
        cube([spacer_length, spacer_width, spacer_height]);
}

module support_mount(show_ghost=false) {
    if (show_ghost) %alignds420();
    difference() {
        base_support();
        spacer();
    }
}

module aligned_support_mount(show_ghost=false) {
    translate([0, 0, -servo_height]) 
        rotate([0, 0,  90]) 
            support_mount(show_ghost);
}

// servo "ghost"

aligned_support_mount(true);