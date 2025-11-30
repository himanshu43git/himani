import subprocess
import os

HLPSL_CODE = r"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Three-Factor Authentication Protocol (3FA)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

role user(U, S : agent, Ksu : public_key) played_by U
def=
local
    Pw, Bio, Sc : text
    Nu : text
    Msg1, Msg2, Msg3 : message
init
    state := 0
transition

    1. state = 0
       -> state := 1
       /\ Pw  := new()
       /\ Bio := new()
       /\ Sc  := new()
       /\ Nu  := new()
       /\ Msg1 := {U.h(Pw.Bio.Sc).Nu}_Ksu
       /\ out(Msg1)

    2. state = 1
       /\ in(Msg2)
       /\ Msg2 = {Nu.Ns}_U
       -> state := 2

    3. state = 2
       -> state := 3
       /\ Msg3 := {Ns}_Ksu
       /\ out(Msg3)
       /\ witness(U, S, 3fa_auth, Ns)
end role


role server(U, S : agent, Ksu : public_key) played_by S
def=
local
    Msg1, Msg2, Msg3 : message
    Nu, Ns : text
transition

    1. state = 0
       /\ in(Msg1)
       /\ Msg1 = {U.h(Pw.Bio.Sc).Nu}_Ksu
       -> state := 1
       /\ Ns := new()

    2. state = 1
       -> state := 2
       /\ Msg2 := {Nu.Ns}_U
       /\ out(Msg2)

    3. state = 2
       /\ in(Msg3)
       /\ Msg3 = {Ns}_Ksu
       -> state := 3
       /\ request(S, U, 3fa_auth, Ns)
end role


role session()
def=
local
    U, S : agent
    Ksu : public_key
composition
    user(U, S, Ksu)
    server(U, S, Ksu)
end role


role environment()
def=
const
    u, s : agent,
    ksu : public_key
intruder_knowledge = {u, s, ksu}
composition
    session()
end role


goal
    secrecy_of Pw, Bio, Sc, Nu, Ns
    authentication_on 3fa_auth
end goal
"""


def write_hlpsl_file(filename="3fa_protocol.hlpsl"):
    """Write the HLPSL code to a file."""
    with open(filename, "w") as f:
        f.write(HLPSL_CODE)
    print(f"[OK] HLPSL file created: {filename}")


def run_command(command):
    """Run system command and return output."""
    try:
        result = subprocess.run(command, shell=True, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)


def run_avispa(hlpsl_file="3fa_protocol.hlpsl"):
    if not os.path.exists(hlpsl_file):
        print("[ERROR] HLPSL file not found!")
        return

    # Convert to IF format
    print("\n[+] Running hlpsl2if...")
    output_if = run_command(f"hlpsl2if {hlpsl_file}")
    print(output_if)

    if not os.path.exists("3fa_protocol.if"):
        print("[ERROR] IF file not generated!")
        return

    print("\n[+] Running OFMC backend...")
    ofmc_output = run_command("ofmc 3fa_protocol.if")
    print(ofmc_output)

    print("\n[+] Running CL-AtSe backend...")
    clatse_output = run_command("cl-atse 3fa_protocol.if")
    print(clatse_output)

    print("\n[✓] AVISPA Execution Completed.")


if _name_ == "_main_":
    write_hlpsl_file()
    run_avispa()