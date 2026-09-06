#!/usr/bin/env python3
import sys
import re

def parse_netlist(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # Find (nets ...) block
    nets_match = re.search(r'\(nets(.*?)\)\s*\)\s*$', content, re.DOTALL)
    if not nets_match:
        print(f"Error: nets block not found in {filename}")
        sys.exit(1)
    
    nets_block = nets_match.group(1)
    # Match each (net (code "...") (name "...") (node ...) ...)
    net_entries = re.findall(r'\(net\s+\(code\s+"[^"]*"\)\s+\(name\s+"([^"]+)"\)\s*(.*?)(?=\(net\s|\Z)', nets_block, re.DOTALL)
    
    nets_dict = {}
    for name, nodes_str in net_entries:
        nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', nodes_str)
        nodes_sorted = sorted(nodes)
        nets_dict[name] = nodes_sorted
        
    return nets_dict

def compare(f1, f2):
    n1 = parse_netlist(f1)
    n2 = parse_netlist(f2)
    
    all_names = sorted(set(n1.keys()) | set(n2.keys()))
    diffs = 0
    for name in all_names:
        if name not in n1:
            print(f"[-] Net '{name}' missing from {f1}")
            diffs += 1
        elif name not in n2:
            print(f"[+] Net '{name}' missing from {f2}")
            diffs += 1
        elif n1[name] != n2[name]:
            print(f"[!] Net '{name}' mismatch:")
            print(f"    {f1}: {n1[name]}")
            print(f"    {f2}: {n2[name]}")
            diffs += 1
        else:
            print(f"[✓] Net '{name}': match! ({len(n1[name])} nodes: {n1[name]})")
            
    if diffs == 0:
        print("\n>>> ALL NETS MATCH 100% PERFECTLY! Netlist equivalence verified! <<<")
        return 0
    else:
        print(f"\n>>> FOUND {diffs} NETLIST DIFFERENCES! <<<")
        return 1

if __name__ == "__main__":
    f1 = sys.argv[1] if len(sys.argv) > 1 else "tmp/sch_netlist.net"
    f2 = sys.argv[2] if len(sys.argv) > 2 else "tmp/candidate.net"
    sys.exit(compare(f1, f2))
