import Foundation
import Virtualization

final class MachineDelegate: NSObject, VZVirtualMachineDelegate {
    func guestDidStop(_ virtualMachine: VZVirtualMachine) {
        print("VM_GUEST_STOPPED")
        exit(0)
    }
    func virtualMachine(_ virtualMachine: VZVirtualMachine, didStopWithError error: Error) {
        fputs("VM_ERROR: \(error)\n", stderr)
        exit(1)
    }
}

let loader = VZLinuxBootLoader(kernelURL: URL(fileURLWithPath: CommandLine.arguments[1]))
loader.initialRamdiskURL = URL(fileURLWithPath: CommandLine.arguments[2])
loader.commandLine = "console=hvc0 panic=-1 quiet"
let config = VZVirtualMachineConfiguration()
config.bootLoader = loader
config.cpuCount = 2
config.memorySize = 512 * 1024 * 1024
config.entropyDevices = [VZVirtioEntropyDeviceConfiguration()]
let serial = VZVirtioConsoleDeviceSerialPortConfiguration()
serial.attachment = VZFileHandleSerialPortAttachment(
    fileHandleForReading: .standardInput,
    fileHandleForWriting: .standardOutput
)
config.serialPorts = [serial]
try config.validate()
let delegate = MachineDelegate()
let machine = VZVirtualMachine(configuration: config)
machine.delegate = delegate
machine.start { result in
    if case .failure(let error) = result {
        fputs("VM_START_ERROR: \(error)\n", stderr)
        exit(1)
    }
}
DispatchQueue.main.asyncAfter(deadline: .now() + 120) {
    fputs("VM_TIMEOUT\n", stderr)
    exit(1)
}
dispatchMain()
