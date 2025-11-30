import ns.core
import ns.network
import ns.internet
import ns.applications
import ns.mobility
import ns.wifi

def run_simulation(num_nodes):

    print(f"\nRunning simulation with {num_nodes} sensor nodes...")

    # -------------------------
    # 1. Create nodes
    # -------------------------
    nodes = ns.network.NodeContainer()
    nodes.Create(num_nodes)

    # -------------------------
    # 2. Install WiFi devices
    # -------------------------
    wifi = ns.wifi.WifiHelper()
    wifi.SetRemoteStationManager("ns3::AarfWifiManager")

    phy = ns.wifi.YansWifiPhyHelper.Default()
    channel = ns.wifi.YansWifiChannelHelper.Default()
    phy.SetChannel(channel.Create())

    mac = ns.wifi.WifiMacHelper()
    mac.SetType("ns3::AdhocWifiMac")

    devices = wifi.Install(phy, mac, nodes)

    # -------------------------
    # 3. Install Internet stack
    # -------------------------
    stack = ns.internet.InternetStackHelper()
    stack.Install(nodes)

    address = ns.internet.Ipv4AddressHelper()
    address.SetBase("10.0.0.0", "255.255.255.0")
    interfaces = address.Assign(devices)

    # -------------------------
    # 4. Mobility model
    # -------------------------
    mobility = ns.mobility.MobilityHelper()
    position_alloc = ns.mobility.RandomRectanglePositionAllocator()
    position_alloc.SetX(ns.core.UniformRandomVariable(0, 370))
    position_alloc.SetY(ns.core.UniformRandomVariable(0, 370))

    mobility.SetPositionAllocator(position_alloc)
    mobility.SetMobilityModel(
        "ns3::RandomWalk2dMobilityModel",
        "Mode", ns.core.StringValue("Time"),
        "Time", ns.core.TimeValue(ns.core.Seconds(0.5)),
        "Speed", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=1.3]"),
        "Bounds", ns.core.StringValue("0|370|0|370")
    )

    mobility.Install(nodes)

    # -------------------------
    # 5. Applications (traffic)
    # -------------------------
    port = 5000

    for i in range(1, num_nodes):
        onoff = ns.applications.OnOffHelper(
            "ns3::UdpSocketFactory",
            ns.network.Address(
                ns.network.InetSocketAddress(
                    interfaces.GetAddress(0), port
                )
            ),
        )
        onoff.SetAttribute("PacketSize", ns.core.UintegerValue(100))
        onoff.SetAttribute("DataRate", ns.network.DataRateValue(ns.network.DataRate("100kbps")))
        onoff.SetAttribute("OnTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=1]"))
        onoff.SetAttribute("OffTime", ns.core.StringValue("ns3::ConstantRandomVariable[Constant=0]"))

        # 4-second gap between packets
        onoff.SetAttribute("Interval", ns.core.TimeValue(ns.core.Seconds(4.0)))

        onoff_app = onoff.Install(nodes.Get(i))
        onoff_app.Start(ns.core.Seconds(1.0))
        onoff_app.Stop(ns.core.Seconds(20.0))

    sink = ns.applications.PacketSinkHelper(
        "ns3::UdpSocketFactory",
        ns.network.InetSocketAddress(ns.network.Ipv4Address.GetAny(), port),
    )

    sink_app = sink.Install(nodes.Get(0))
    sink_app.Start(ns.core.Seconds(0.0))
    sink_app.Stop(ns.core.Seconds(20.0))

    # -------------------------
    # 6. Run simulation
    # -------------------------
    ns.core.Simulator.Stop(ns.core.Seconds(20))
    ns.core.Simulator.Run()
    ns.core.Simulator.Destroy()

    # -------------------------
    # 7. Output
    # -------------------------
    print(f"Simulation with {num_nodes} nodes completed.")

# -----------------------------------------
# Run scenarios for 20, 30, and 40 nodes
# -----------------------------------------
for n in [20, 30, 40]:
    run_simulation(n)