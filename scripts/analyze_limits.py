#!/usr/bin/env python3
"""
Dog Fence Perimeter Scaling Analysis
Calculates the physical and electrical limits for scaling the 3-core 2.5mm²
fence system beyond 4km, maintaining milestones every 100m.
Pure Python standard library implementation (no external packages).
"""

import math

def simulate_test_mode(L_km, V_supply=36.0, r_core=7.0, R_rung=2200.0, V_th=2.8, dx=0.1):
    """
    Solves the discrete resistor ladder network for TEST mode using relaxation.
    
    Wires A & C run from 0 to L in parallel: resistance per segment = (r_core / 2) * dx.
    Wire B runs from 0 to L: resistance per segment = r_core * dx.
    
    At Shed (x = 0):
      Wires A & C connected to +V_supply.
      Wire B is floating (Start B is disconnected).
    
    At Far End (x = L):
      Wires A & C are floating (End A & C disconnected).
      Wire B is connected to 0V (DC Return).
      
    Milestones at x_k = k * dx for k = 1 to N (N = L / dx).
    Each milestone has 2 rungs in parallel:
      I_box(k) = 2 * max(0.0, (V_AC[k] - V_B[k] - V_th) / R_rung)
    """
    N = int(round(L_km / dx))
    r_AC_seg = (r_core / 2.0) * dx
    r_B_seg = r_core * dx
    R_box = R_rung / 2.0  # two rungs in parallel
    
    g_AC = 1.0 / r_AC_seg
    g_B = 1.0 / r_B_seg
    g_box = 1.0 / R_box
    
    V_AC = [V_supply] * (N + 1)
    V_B = [0.0] * (N + 1)
    
    # Successive over-relaxation (SOR) / Gauss-Seidel
    omega = 1.2
    for it in range(10000):
        max_diff = 0.0
        
        # AC[0] is fixed at V_supply
        V_AC[0] = V_supply
        
        # Internal AC nodes k = 1 .. N-1
        for k in range(1, N):
            # Connections: to k-1 (g_AC), to k+1 (g_AC), and to B[k] (g_box if active)
            vd = V_AC[k] - V_B[k]
            active = (vd > V_th)
            G_sum = 2.0 * g_AC + (g_box if active else 0.0)
            I_sum = g_AC * (V_AC[k-1] + V_AC[k+1]) + ((g_box * (V_B[k] + V_th)) if active else 0.0)
            v_target = I_sum / G_sum
            v_new = V_AC[k] + omega * (v_target - V_AC[k])
            diff = abs(v_new - V_AC[k])
            if diff > max_diff: max_diff = diff
            V_AC[k] = v_new
            
        # End AC node k = N (floating, only connected to N-1 and B[N])
        vd = V_AC[N] - V_B[N]
        active = (vd > V_th)
        G_sum = g_AC + (g_box if active else 0.0)
        I_sum = g_AC * V_AC[N-1] + ((g_box * (V_B[N] + V_th)) if active else 0.0)
        v_target = I_sum / G_sum
        v_new = V_AC[N] + omega * (v_target - V_AC[N])
        diff = abs(v_new - V_AC[N])
        if diff > max_diff: max_diff = diff
        V_AC[N] = v_new
        
        # B[0] node (floating at shed, connected to B[1] only, no milestone at k=0)
        # Note: B[0] has no milestone across it since milestones are at k=1..N
        # So V_B[0] is simply equal to V_B[1]
        diff = abs(V_B[1] - V_B[0])
        if diff > max_diff: max_diff = diff
        V_B[0] = V_B[1]
        
        # Internal B nodes k = 1 .. N-1
        for k in range(1, N):
            vd = V_AC[k] - V_B[k]
            active = (vd > V_th)
            G_sum = 2.0 * g_B + (g_box if active else 0.0)
            I_sum = g_B * (V_B[k-1] + V_B[k+1]) + ((g_box * (V_AC[k] - V_th)) if active else 0.0)
            v_target = I_sum / G_sum
            v_new = V_B[k] + omega * (v_target - V_B[k])
            diff = abs(v_new - V_B[k])
            if diff > max_diff: max_diff = diff
            V_B[k] = v_new
            
        # B[N] is fixed at 0.0V (End B connected to 0V)
        V_B[N] = 0.0
        
        if max_diff < 1e-6:
            break
            
    # Calculate currents and statistics
    I_supply = (V_AC[0] - V_AC[1]) * g_AC
    
    V_diffs = []
    I_leds = []
    for k in range(1, N + 1):
        vd = V_AC[k] - V_B[k]
        V_diffs.append(vd)
        i_box = 2.0 * max(0.0, (vd - V_th) / R_rung)
        i_led = i_box / 2.0
        I_leds.append(i_led * 1000.0)  # mA
        
    return {
        "N": N,
        "I_supply_A": I_supply,
        "V_diff_min": min(V_diffs),
        "V_diff_max": max(V_diffs),
        "I_led_min_mA": min(I_leds),
        "I_led_max_mA": max(I_leds),
        "min_loc_km": (V_diffs.index(min(V_diffs)) + 1) * dx,
        "V_AC_end": V_AC[N],
        "V_B_start": V_B[0]
    }

def simulate_dual_feed_test_mode(L_km, V_supply=36.0, r_core=7.0, R_rung=2200.0, V_th=2.8, dx=0.1):
    """
    Simulates dual-ended feed (feeding +V_supply into Start A/C AND End A/C,
    and 0V into Start B AND End B).
    """
    N = int(round(L_km / dx))
    r_AC_seg = (r_core / 2.0) * dx
    r_B_seg = r_core * dx
    R_box = R_rung / 2.0
    
    g_AC = 1.0 / r_AC_seg
    g_B = 1.0 / r_B_seg
    g_box = 1.0 / R_box
    
    V_AC = [V_supply] * (N + 1)
    V_B = [0.0] * (N + 1)
    
    omega = 1.2
    for it in range(10000):
        max_diff = 0.0
        
        # Fixed endpoints:
        V_AC[0] = V_supply
        V_AC[N] = V_supply
        V_B[0] = 0.0
        V_B[N] = 0.0
        
        for k in range(1, N):
            vd = V_AC[k] - V_B[k]
            active = (vd > V_th)
            G_sum = 2.0 * g_AC + (g_box if active else 0.0)
            I_sum = g_AC * (V_AC[k-1] + V_AC[k+1]) + ((g_box * (V_B[k] + V_th)) if active else 0.0)
            v_target = I_sum / G_sum
            v_new = V_AC[k] + omega * (v_target - V_AC[k])
            diff = abs(v_new - V_AC[k])
            if diff > max_diff: max_diff = diff
            V_AC[k] = v_new
            
            G_sum = 2.0 * g_B + (g_box if active else 0.0)
            I_sum = g_B * (V_B[k-1] + V_B[k+1]) + ((g_box * (V_AC[k] - V_th)) if active else 0.0)
            v_target = I_sum / G_sum
            v_new = V_B[k] + omega * (v_target - V_B[k])
            diff = abs(v_new - V_B[k])
            if diff > max_diff: max_diff = diff
            V_B[k] = v_new
            
        if max_diff < 1e-6:
            break
            
    I_start = (V_AC[0] - V_AC[1]) * g_AC
    I_end = (V_AC[N] - V_AC[N-1]) * g_AC
    I_supply = I_start + I_end
    
    V_diffs = []
    I_leds = []
    for k in range(1, N):
        vd = V_AC[k] - V_B[k]
        V_diffs.append(vd)
        i_box = 2.0 * max(0.0, (vd - V_th) / R_rung)
        i_led = i_box / 2.0
        I_leds.append(i_led * 1000.0)
        
    return {
        "N": N,
        "I_supply_A": I_supply,
        "V_diff_min": min(V_diffs),
        "I_led_min_mA": min(I_leds),
        "I_led_max_mA": max(I_leds),
        "min_loc_km": (V_diffs.index(min(V_diffs)) + 1) * dx
    }


def main():
    print("=" * 95)
    print("DOG FENCE SYSTEM SCALABILITY STUDY (100m Milestone Spacing, 3-Core 2.5mm² Cable)")
    print("=" * 95)
    
    lengths = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 18.0, 20.0]
    
    print(f"\n--- 1. DC TEST MODE SIMULATION (V_supply = 36V DC, Fuse = 2.0A, R_rung = 2.2kΩ) ---")
    print(f"{'Length':<8} {'Boxes':<6} {'I_total':<10} {'I_LED min':<12} {'I_LED max':<12} {'V_diff min':<12} {'Min Loc':<10} {'Fuse Status':<12}")
    print(f"{'(km)':<8} {'(qty)':<6} {'(A)':<10} {'(mA)':<12} {'(mA)':<12} {'(V)':<12} {'(km)':<10} {'(2A Limit)':<12}")
    print("-" * 88)
    
    for L in lengths:
        res = simulate_test_mode(L, V_supply=36.0, r_core=7.0)
        fuse_status = "OK" if res['I_supply_A'] < 2.0 else "BLOWS (>2A)"
        print(f"{L:<8.1f} {res['N']:<6d} {res['I_supply_A']:<10.3f} {res['I_led_min_mA']:<12.2f} {res['I_led_max_mA']:<12.2f} {res['V_diff_min']:<12.2f} {res['min_loc_km']:<10.1f} {fuse_status:<12}")
        
    print(f"\n--- 2. DC TEST MODE (DUAL-ENDED FEED: +36V at Start & End A/C, 0V at Start & End B) ---")
    print(f"{'Length':<8} {'Boxes':<6} {'I_total':<10} {'I_LED min':<12} {'I_LED max':<12} {'V_diff min':<12} {'Min Loc':<10}")
    print(f"{'(km)':<8} {'(qty)':<6} {'(A)':<10} {'(mA)':<12} {'(mA)':<12} {'(V)':<12} {'(km)':<10}")
    print("-" * 75)
    for L in [4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 25.0, 30.0]:
        res = simulate_dual_feed_test_mode(L, V_supply=36.0, r_core=7.0)
        print(f"{L:<8.1f} {res['N']:<6d} {res['I_supply_A']:<10.3f} {res['I_led_min_mA']:<12.2f} {res['I_led_max_mA']:<12.2f} {res['V_diff_min']:<12.2f} {res['min_loc_km']:<10.1f}")
        
    print(f"\n--- 3. DC TEST MODE WITH 48V DC SUPPLY (Forward Loop, 48V DIN Rail PSU) ---")
    print(f"{'Length':<8} {'Boxes':<6} {'I_total':<10} {'I_LED min':<12} {'I_LED max':<12} {'V_diff min':<12} {'P_res max':<12}")
    print(f"{'(km)':<8} {'(qty)':<6} {'(A)':<10} {'(mA)':<12} {'(mA)':<12} {'(V)':<12} {'(W)':<12}")
    print("-" * 80)
    for L in [4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 25.0]:
        res = simulate_test_mode(L, V_supply=48.0, r_core=7.0)
        p_max = ((res['I_led_max_mA'] / 1000.0) ** 2) * 2200.0
        print(f"{L:<8.1f} {res['N']:<6d} {res['I_supply_A']:<10.3f} {res['I_led_min_mA']:<12.2f} {res['I_led_max_mA']:<12.2f} {res['V_diff_min']:<12.2f} {p_max:<12.2f}")

    print(f"\n--- 3. SMARTFENCE RF RUN MODE LOOP IMPEDANCE & CAPACITANCE ---")
    print(f"{'Length':<8} {'Loop DC R':<12} {'Loop Induct':<14} {'XL @ 10.7kHz':<16} {'GDT Earth Cap':<16} {'Cable Earth Cap':<16}")
    print(f"{'(km)':<8} {'(Ω)':<12} {'(mH est)':<14} {'(Ω)':<16} {'(pF)':<16} {'(nF est)':<16}")
    print("-" * 85)
    for L in [1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0, 25.0, 30.0]:
        r_loop = (7.0 / 3.0) * L
        L_mH = 1.35 * L
        XL_10k7 = 2 * math.pi * 10700 * (L_mH * 1e-3)
        # GDT capacitance: 3 common-mode GDTs per box = 4.5 pF per box
        c_gdt_total = (L * 10) * 1.5 * 3
        # Cable capacitance to soil: approx 80 pF/m = 80 nF/km
        c_cable_earth = 80.0 * L
        print(f"{L:<8.1f} {r_loop:<12.2f} {L_mH:<14.2f} {XL_10k7:<16.1f} {c_gdt_total:<16.1f} {c_cable_earth:<16.1f}")

if __name__ == "__main__":
    main()
