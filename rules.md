# A Game of War
**Designed by Guy Debord**

### 1. Overview
*A Game of War* is a strategy game for two players (North and South) simulating military conflict. Unlike Chess, the focus is not just on capturing pieces, but on maintaining a **Lines of Communication (LOC)** network.

**The Objective:** Destroy the enemy by achieving one of the following:
1.  Destroying both enemy Arsenals.
2.  Destroying all enemy mobile units.
3.  Destroying both enemy Relays, forcing all remaining enemy units offline.

### 2. The Battlefield
The game is played on a grid of 500 squares (20 x 25). The board is divided into North and South territories. Each territory contains:
*   **1 Mountain Range:** 9 squares of impassable terrain.
*   **1 Mountain Pass:** Allows travel through mountains.
*   **2 Arsenals:** The immobile power sources for your communications.
*   **3 Fortresses:** Defensive structures.

**Terrain Rules:**
*   **Mountains:** Impassable. They block movement, attacks, and Lines of Communication.
*   **Mountain Passes:** Traversable. They do **not** block Lines of Communication. They provide a **+2 Defense** bonus to Infantry and Cannons.
*   **Fortresses:** Traversable. They do **not** block Lines of Communication. They are neutral (any unit can occupy them). They provide a **+4 Defense** bonus to Infantry and Cannons. Fortresses cannot be destroyed.

### 3. Lines of Communication (The Network)
This is the game's most critical mechanic. Your units rely on a "network" to function.
*   **The Source:** Your two Arsenals radiate Lines of Communication vertically, horizontally, and diagonally (45º).
*   **Relays:** You have mobile Relay units that can reflect/extend these lines.
*   **Staying Online:** A unit is considered "Online" if it is in direct connection with an Arsenal or is adjacent to a friendly unit that is Online.
*   **Going Offline:** If a unit is not connected, it goes "Offline."
    *   **Offline Units:** Cannot move, cannot attack, and cannot defend themselves (they have 0 defense).
    *   *Exception:* An offline unit still receives defensive support from adjacent friendly units.
    *   *Relays:* Unlike other units, Relays **can** move while offline. However, a Relay only extends the communication network if it is itself Online.

**Blocking the Network:**
Lines of Communication are blocked by Mountains and **Enemy Units**.
*   Note: Lines are **not** blocked by Mountain Passes or Enemy Relays.

### 4. Units & Stats
Each player starts with the same force. All stats are listed as **Attack / Defense / Movement / Range**.

**Headquarters**
*   **Arsenal:** Immobile. No Defense. Radiates communication.
    *   *Special Rule:* An enemy destroys your Arsenal simply by moving onto it (if empty). This counts as the attack for that turn. Relays cannot destroy Arsenals as they have 0 Attack.

**Communication Units**
*   **Relay:** **Atk 0 / Def 1 / Move 1 / Range 0**.
*   **Swift Relay:** **Atk 0 / Def 1 / Move 2 / Range 0**.

**Combat Units**
*   **Infantry (x9):** **Atk 4 / Def 6 / Move 1 / Range 2**.
    *   Sturdy and reliable.
*   **Cavalry (x4):** **Atk 4 / Def 5 / Move 2 / Range 2**.
    *   Fast. Special Ability: **Charge**.
*   **Cannon (x1):** **Atk 5 / Def 8 / Move 1 / Range 3**.
    *   Slow but long-ranged and hard to kill.
*   **Swift Cannon (x1):** **Atk 5 / Def 8 / Move 2 / Range 3**.
    *   A faster version of the Cannon.

### 5. Setup
1.  Each player places their units freely within their own territory.
2.  Opponent set-ups are hidden until the game begins.
3.  Roll a die to determine who moves first.

### 6. Turn Sequence
A turn consists of two phases: **Movement** and **Combat**.

**A. Movement Phase**
*   The player may move **up to 5 units** per turn.
*   You may move fewer than 5.
*   A unit cannot move more than once per turn.
*   *Relays:* Can move even if offline.
*   *All others:* Must be online to move. (They may move *into* an offline position, but if they end their turn offline, they will be unable to move next turn).

**B. Combat Phase**
*   The player may perform **1 Attack** per turn.
*   Attacking is optional.
*   You may attack any enemy unit within range.

**How Attack & Defense Work:**
Combat is calculated by comparing power numbers along straight lines (vertical, horizontal, or diagonal).

1.  **Calculate Attack Power:** Sum the Attack stats of **all** your units in a direct line with the target enemy unit.
2.  **Calculate Defense Power:** Sum the Defense stats of **all** enemy units in a direct line supporting the target.
3.  **Compare the Totals:**
    *   **Offense ≤ Defense:** The attack fails. The unit is secure.
    *   **Offense = Defense + 1:** **Forced Retreat.** The defender must move that unit at the start of their next turn. The retreating unit cannot attack during that turn. If there is no valid square to retreat to, the unit is captured (destroyed).
    *   **Offense ≥ Defense + 2:** **Capture.** The defending unit is destroyed immediately.

**Cavalry Charge:**
*   If a Cavalry unit is adjacent to the target, its Attack power increases from 4 to **7**.
*   Up to four Cavalry in a line can stack this bonus, raising the total attack up to **28**.

### 7. Special Rules & Restrictions
*   **Occupation:** Only one unit may occupy a square at a time (Arsenals, Fortresses, and Passes included).
*   **Relay Attacks:** Relays have 0 Attack. They cannot attack or destroy Arsenals.
*   **Cavalry Restrictions:**
    *   Cavalry **cannot** charge if the target is in a Fortress or Mountain Pass.
    *   Cavalry **cannot** charge if they are currently inside a Fortress.
    *   Cavalry **can** charge if they are inside a Mountain Pass.

### 8. Summary of Victory
To win the game, you must completely destroy the enemy's capacity to fight. You win instantly if you accomplish **one** of the following:
1.  **Destruction of Arsenals:** You capture/destroy both enemy Arsenals.
2.  **Total Annihilation:** You destroy all enemy combat units.
3.  **Network Collapse:** You destroy both enemy Relays, and all remaining enemy units are forced Offline.