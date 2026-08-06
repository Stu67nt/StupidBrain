package org.example;

/*
GOAL:
Find a seed with a ruined portal within 100 blocks of spawn meeting following criteria.
- Should contain at least 27 iron nuggets
- Contains one of fire charge, flint and steel,
- 6 or more obsidian
 */

public class Main {
     static void main() {
        DesertTempleFilter finder = new DesertTempleFilter(0L, 100000000L);
        finder.run();
    }
}
