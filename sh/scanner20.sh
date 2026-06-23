#!/data/data/com.termux/files/usr/bin/bash

GREEN="\033[1;32m"
RED="\033[1;31m"
YELLOW="\033[1;33m"
CYAN="\033[1;36m"
NC="\033[0m"

INPUT="ips.txt"

SCORED="scored.db"

FAST="fast.txt"
STABLE="stable.txt"
WEAK="weak.txt"

CLEAN="clean.txt"
PORT_OUT="port.txt"

PORT=443
THREADS=70
TOP=50
MAX_LATENCY=400

banner() {
clear
echo -e "${CYAN}"
echo "=================================="
echo "     FINAL GOD AI MAX ENGINE"
echo "=================================="
echo -e "${NC}"
}

test_ip() {
    ip=$1

    # ---------------- TCP TEST ----------------
    t1=$(date +%s%N)
    timeout 1 bash -c "echo > /dev/tcp/$ip/$PORT" 2>/dev/null
    if [ $? -ne 0 ]; then
        return
    fi
    t2=$(date +%s%N)

    ms=$(( (t2 - t1) / 1000000 ))

    # ---------------- JITTER CHECK ----------------
    t3=$(date +%s%N)
    timeout 1 bash -c "echo > /dev/tcp/$ip/$PORT" 2>/dev/null
    t4=$(date +%s%N)

    ms2=$(( (t4 - t3) / 1000000 ))
    jitter=$(( ms > ms2 ? ms - ms2 : ms2 - ms ))

    # ---------------- STABILITY FACTOR ----------------
    stability=$((100 - jitter*2))

    if [ "$stability" -lt 0 ]; then
        stability=0
    fi

    # ---------------- AI SCORE ----------------
    score=$((100 - (ms/5) - (jitter*3) + (stability/5)))

    # penalties
    if [ "$ms" -gt 200 ]; then score=$((score-10)); fi
    if [ "$ms" -gt 300 ]; then score=$((score-20)); fi
    if [ "$ms" -gt 400 ]; then score=$((score-30)); fi

    if [ "$score" -lt 0 ]; then score=0; fi

    if [ "$ms" -lt "$MAX_LATENCY" ]; then
        echo "$score $ms $jitter $ip" >> "$SCORED"
    fi
}

load_input() {
    if [ ! -f "$INPUT" ]; then
        cat > "$INPUT" <<EOF
104.16.0.1
104.17.0.1
104.18.0.1
EOF
    fi
}

start_scan() {

    > "$SCORED"
    > "$FAST"
    > "$STABLE"
    > "$WEAK"
    > "$CLEAN"
    > "$PORT_OUT"

    load_input

    echo -e "${CYAN}[*] FINAL GOD AI SCAN STARTED...${NC}"

    i=0
    while read ip; do
        ((i=i%THREADS)); ((i++==0)) && wait
        test_ip "$ip" &
    done < "$INPUT"

    wait

    echo -e "${YELLOW}\n[*] AI ranking + classification...${NC}"

    sort -nr "$SCORED" | while read score ms jitter ip; do

        if [ "$score" -ge 80 ]; then
            echo "$ip" >> "$FAST"
        elif [ "$score" -ge 50 ]; then
            echo "$ip" >> "$STABLE"
        else
            echo "$ip" >> "$WEAK"
        fi

    done

    cat "$FAST" | head -n "$TOP" > "$CLEAN"

    while read ip; do
        echo "$ip:$PORT" >> "$PORT_OUT"
    done < "$CLEAN"

    echo -e "${GREEN}\n===== FAST IPs =====${NC}"
    cat "$FAST"

    echo -e "${YELLOW}\n===== STABLE IPs =====${NC}"
    cat "$STABLE"

    echo -e "${RED}\n===== WEAK IPs =====${NC}"
    cat "$WEAK"

    echo -e "${GREEN}\n===== FINAL TOP CLEAN =====${NC}"
    cat "$CLEAN"

    echo -e "${YELLOW}\n===== PORT OUTPUT =====${NC}"
    cat "$PORT_OUT"

    # clipboard
    cat "$CLEAN" "$PORT_OUT" | termux-clipboard-set

    echo ""
    echo "[✓] FINAL OUTPUT COPIED TO CLIPBOARD"
    echo "[✓] GOD MODE COMPLETE"
}

menu() {
while true; do
    banner
    echo "1) START FINAL GOD AI SCAN"
    echo "2) EXIT"
    echo
    read -p "SELECT: " c

    case $c in
        1) start_scan; read -p "ENTER..." ;;
        2) exit 0 ;;
    esac
done
}

menu
