from lxml import etree
import pkg_resources


def volume(
    name,
    capacity=0,
    format_=None,
    ):
    root = etree.Element('volume')
    etree.SubElement(root, 'name').text = name
    etree.SubElement(root, 'capacity').text = '{0:d}'.format(capacity)
    etree.SubElement(root, 'allocation').text = '0'
    target = etree.SubElement(root, 'target')
    if format_ is None:
        format_ = 'qcow2'
    etree.SubElement(target, 'format', type=format_)
    return root


def volume_clone(
    name,
    parent_vol,
    ):
    (_type_, capacity, _allocation) = parent_vol.info()
    root = volume(name=name, capacity=capacity)

    backing = etree.SubElement(root, 'backingStore')
    etree.SubElement(backing, 'format', type='qcow2')
    etree.SubElement(backing, 'path').text = parent_vol.key()

    return root


def domain(
    name,
    disk_key,
    iso_key,
    ):
    with pkg_resources.resource_stream('downburst', 'template.xml') as f:
        tree = etree.parse(f)
    (domain,) = tree.xpath('/domain')

    n = etree.SubElement(domain, 'name')
    n.text = name

    # <disk type='file' device='disk'>
    #   <driver name='qemu' type='qcow2'/>
    #   <source file='/var/lib/libvirt/images/NAME.img'/>
    #   <target dev='vda' bus='virtio'/>
    # </disk>
    (devices,) = tree.xpath('/domain/devices')
    disk = etree.SubElement(devices, 'disk', type='file', device='disk')
    etree.SubElement(disk, 'driver', name='qemu', type='qcow2')
    etree.SubElement(disk, 'source', file=disk_key)
    etree.SubElement(disk, 'target', dev='vda', bus='virtio')

    # <disk type='file' device='cdrom'>
    #   <driver name='qemu' type='raw'/>
    #   <source file='/var/lib/libvirt/images/cloud-init.chef03.iso'/>
    #   <target dev='hdc' bus='ide'/>
    #   <readonly/>
    # </disk>
    disk = etree.SubElement(devices, 'disk', type='file', device='cdrom')
    etree.SubElement(disk, 'driver', name='qemu', type='raw')
    etree.SubElement(disk, 'source', file=iso_key)
    etree.SubElement(disk, 'target', dev='hdc', bus='ide')

    return tree