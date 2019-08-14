from enum import Flag, IntEnum, auto
from itertools import chain

SAFE_LOCATIONS = [b'Nexus', b'Market', b'Vault']
NO_ACTION = [b'Market']
NO_PICKUP = [b'Vault']


class STATUS(Flag):
    B1 = auto()
    SILENT = auto()
    B3 = auto()
    SLOW = auto()
    B5 = auto()  # skull
    SLOW_ATTACK = auto()
    STAR = auto()  # NO ATTACK
    BLIND = auto()
    HALLUCINATING = auto()
    DRUNK = auto()
    CONFUSED = auto()
    B12 = auto()
    INVISIBLE = auto()
    PARALYZED = auto()
    SPEEDY = auto()
    BLEEDING = auto()
    B17 = auto()
    HEALING = auto()
    DAMAGING = auto()
    BERSERK = auto()
    DISABLED = auto()  # GRAY
    BLACK_WHITE = auto()
    B23 = auto()
    B24 = auto()
    INVULN = auto()
    BROWN_ARMOR = auto()
    CROSS = auto()
    IM_PET = auto()
    SPEEDY2 = auto()
    UNSTABLE = auto()
    DARKNESS = auto()
    B32 = auto()


"""
0x27 = fame
"""
MAPPING = {
    0x00: ('max_hp', 'value'),
    0x01: ('hp', 'value'),
    0x03: ('max_mp', 'value'),
    0x04: ('mp', 'value'),
    0x08: ('item_1', 'value'),
    0x09: ('item_2', 'value'),
    0x0a: ('item_3', 'value'),
    0x0b: ('item_4', 'value'),
    0x0c: ('slot_1', 'value'),
    0x0d: ('slot_2', 'value'),
    0x0e: ('slot_3', 'value'),
    0x0f: ('slot_4', 'value'),
    0x10: ('slot_5', 'value'),
    0x11: ('slot_6', 'value'),
    0x12: ('slot_7', 'value'),
    0x13: ('slot_8', 'value'),
    0x14: ('ATT', 'value'),
    0x15: ('DEF', 'value'),
    0x16: ('SPD', 'value'),
    0x1a: ('VIT', 'value'),
    0x1b: ('WIS', 'value'),
    0x1c: ('DEX', 'value'),
    0x1d: ('status', 'value'),
    0x1f: ('name', 'name'),
    0x26: ('0x26', 'name'),
    0x36: ('0x36', 'name'),
    0x3e: ('clan', 'name'),
    0x47: ('bag_1', 'value'),
    0x48: ('bag_2', 'value'),
    0x49: ('bag_3', 'value'),
    0x4a: ('bag_4', 'value'),
    0x4b: ('bag_5', 'value'),
    0x4c: ('bag_6', 'value'),
    0x4d: ('bag_7', 'value'),
    0x4e: ('bag_8', 'value'),
    0x63: ('0x63', 'name'),
}

# SLOTS + BAG
INV = range(0xc, 0x14)
SLOTS_NAMES = list(chain(range(0x8, 0xc), INV, range(0x47, 0x4f)))
SLOTS = list(
    zip(
        SLOTS_NAMES,
        range(20)
    ),
)
SLOTS_ID_TO_IDX = dict(SLOTS)
# SLOTS = list(range(0xc, 0x14))


class ITEM(IntEnum):
    ATT = 0xa1f
    DEF = 0xa20
    SPD = 0xa21
    VIT = 0xa34
    WIS = 0xa35
    DEX = 0xa4c
    HP = 0xae9
    MANA = 0xaea
    SKULL_TORMENT = 2321
    SKULL_CHOCO = 22154
    ATT_2X = 9064
    HP_2X = 9070
    VIT_2X = 9067
    MYST_COIN = 22066
    MYST_COIN_3 = 22134
    INC_RING = 23020  # imm to flame
    STAFF_T14 = 2320
    ROBE_INCUMB_F5 = 21774

    SPECIAL_CRATE = 21309
    ITEM_CRATE = 21310
    POTION_CRATE = 21311
    GREEN_CRATE = 21334
    COIN1 = 21821
    COIN2 = 21822
    COIN3 = 21823
    COIN4 = 21824
    COIN5 = 21825
    COIN6 = 21826
    MYSTIC_T5 = 0xa46
    DAGGER_T7 = 0xa18
    DEF_T3 = 0xab8
    STAFF_T8 = 2719
    BOOK_T4 = 2611
    SWORD_T8 = 2690
    LARMOR_T8 = 2574
    SCEPTER_T3 = 2864
    KAT_T8 = 3148
    SUR_T3 = 3158
    STAFF_T7 = 2718
    LARMOR_T9 = 2771
    BOW_T8 = 2590
    ROBE_T8 = 2780
    DEX_T3 = 2748
    SUR_T4 = 3159
    HEALTH_T4 = 2757
    ARMOR_T9 = 2579
    WAND_T7 = 2784
    HELM_T4 = 2666
    WAND_T8 = 2567
    ATT_T4 = 2751
    HELM_T3 = 2665
    DAG_T0 = 2580
    POISON_T0 = 2723
    ARMOR_T15 = 2499
    QUIVER_T3 =  2782
    POISON_T5 = 2728
    SPD_T3 = 2745
    SWORD_T7 = 2562
    ROBE_T9 = 2656
    SEAL_T3 = 2778
    DEF_T4 = 2752
    ATT_T3 = 2743
    QUIVER_T0 = 2657
    PRISM_T4 = 2847
    MP_T4 = 2758
    SKULL_T5 = 2735
    KAT_T7 = 3147
    SKULL_T3 = 2733
    ARMOR_T8 = 2578
    WAND_F3_DISP = 9084
    HP_T3 = 2749
    SEAL_T4 = 2644
    POISON_T4 = 2727
    SHIELD_T4 = 2571
    WIS_T3 = 2747
    ARB_T7 = 2618
    SPD_T4 = 2753
    QUIVER_T4 = 2660
    POISON_T3 = 2726
    DAG_T8 = 2585
    TRAP_T4 = 2741
    PRISM_T3 = 2846
    ORB_T4 = 2629
    DEX_T4 = 2756
    SCEPTER_T4 = 2865
    VIT_T3 = 2746
    DAG_T9 = 2696
    CLOAK_T4 = 2649
    BOOK_T3 = 2776
    SWORD_UT_SKULL_F3 = 8732
    SPELL_T3 = 2773
    VIT_T4 = 2754
    WIS_T4 = 2755
    SUR_T5 = 3160
    KAT_UT_SALJU_F3 = 9087
    MP_T3 = 2750
    SEAL_T5 = 2645
    CLOAK_T3 = 2779
    SWORD_UT_FROSTBITE_F3 = 9612
    SWORD_T0 = 2560
    BACKPACK = 3180
    BOOK_T0 = 2609
    MANA_POTION = 2595
    WAND_UT_HORR_F3 = 3859
    ORB_T3 = 2628
    KAT_UT_DIAM_F1 = 8842
    TRAP_T3 = 2740
    CHAR_UNLOCKER = 810
    CHEST_UNLOCKER = 811
    GHOST_RUM = 3109
    KAT_T10 = 3150
    SHIELD_T3 = 2767
    HP_POTION = 2594
    ALCHEM = 21634
    ROBE_T14 = 2511
    KAT_T12 = 3152
    KAT_T6 = 3146
    WAND_T10 = 2694
    DAG_UT_RABBIT_F3 = 2201
    SPELL_T4 = 2774
    SCEPTER_T5 = 2866
    SKULL_T4 = 2734
    WANT_UT_TERROR_F3 = 3856
    BOW_T0 = 2586
    TRAP_T0 = 2737
    KAT_T9 = 3149
    HELMET_T0 = 2662
    QUIVER_T1 = 2658
    BOOK_T1 = 2775
    LARMOR_T5 = 2768
    BOT_UT_NIGHTM_F3 = 3858
    CLOAK_T5 = 2785
    DAG_UT_ICICLE_F3 = 9085
    ROBE_T10 = 2708
    LARMOR_T11 = 2703
    WAND_T9 = 2693
    BOW_UT_FRONTE_F3 = 9610
    ROBE_T5 = 2688
    BOOT_T5 = 2651
    WAND_UT_BALL_F3 = 8854
    QUEST_CHEST = 3468
    ECOIN1 = 22132
    ROBE_T6 = 2654
    DEX_T1 = 2637
    ARMOR_T10 = 2705
    ARMOR_T11 = 2706
    WAND_T3 = 2565
    SWORD_T9 = 2691
    STAFF_T3 = 2714
    ORB_T1 = 2626
    ROBE_T4 = 2687
    WANT_UT_ROSE_F1 = 8844
    KAT_T5 = 3145
    LARMOR_T10 = 2702
    CLOAK_T0 = 2646
    SWORD_T10 = 2692
    SPELL_T1 = 2772
    HELMET_T1 = 2663
    DAG_T4 = 2676
    ARMOR_T4 = 2685
    ROBE_T3 = 2653
    SWORD_T3 = 2561
    MAGN_RECEIPT = 21633
    KAT_UT_CLEAVER_F3 = 3860
    HELMET_T5 = 2667
    FUEL_PUMP = 22404
    FUEL_CART = 22403
    VIT_T1 = 2614
    PRISM_T1 = 2844
    SPD_T1 = 2598
    LARMOR_T6 = 2769
    SHIELD_T1 = 2569
    XP_BOOSTER = 3179
    BOW_T10 = 2700
    FLAME_IN_BOTTLE = 21775
    SEAL_0 = 2642
    DAG_UT_HEARTH_F1 = 8845
    STAFF_T6 = 2717
    SPELL_T2 = 2607
    DAG_T3 = 2675
    SPELL_T0 = 2606
    STAFF_T9 = 2720
    STAFF_UT_ADOR_F1 = 8843
    DAG_T5 = 2582
    SWORD_UT_VINE_F1 = 8846
    ANT_POTION = 21869
    ARMOR_T12 = 2707
    KAT_T11 = 3151
    DAG_UT_TALON_F3 = 3857
    ROBE_T7 = 2655
    POISON_T1 = 2724
    ORB_T2 = 2627
    DAG_T6 = 2583
    TRAP_T1 = 2738
    DEF_T1 = 2597
    BOW_T6 = 2589
    BOW_T12 = 2818
    MP_T1 = 2600
    GROWTH_POTION = 21868
    ARMOR_T3 = 2684
    CLOAK_T2 = 2648
    SPELL_T5 = 2608
    RIGGED_ALCHEMIST = 21870  # GIVE ALL POTIONS
    STAFF_UT_LALA_F3 = 9086
    BOW_UT_CUPID_F1 = 8847
    WIS_T1 = 2615
    STAFF_T4 = 2715
    LARMOR_T4 = 2682
    STAFF_T5 = 2716
    WAND_T4 = 2673
    LARMOR_T3 = 2681
    SCEPTER_T1 = 2862
    KAT_T2 = 3142
    HELMET_T2 = 2664
    FLAME_SEEDS = 23019
    TRAP_T5 = 2742
    HP_T6 = 2985
    DEX_2X = 9069
    SWORD_UT_ICE_F3 = 5846
    ROBE_T11 = 2709
    KAT_T4 = 3144
    LARMOR_T1 = 2680
    BOW_T9 = 2699
    SHIELD_T5 = 2572
    ARMOR_T5 = 2576
    SPD_T2 = 2603
    ATT_T1 = 2596
    SWORD_T6 = 2620
    ARMOR_T6 = 2577
    STAFF_T0 = 2711
    KAT_T3 = 3143
    STAFF_T10 = 2721
    LARMOR_T2 = 2573
    ROBE_T12 = 2710
    QUIVER_T5 = 2661
    ARMOR_T7 = 2783
    LARMOR_T7 = 2770
    ROBE_ST_TOGA_F5 = 2526
    PRISM_5 = 2848
    CLOAK_T1 = 2647
    VIT_T5 = 2762
    KAT_T13 = 586
    LUCKY_BOX = 21647
    LUCKY_KEY = 21650
    BOW_T4 = 2679
    STAFF_ST_FIRE_F5 = 21772
    WAND_T6 = 2621
    FIRE_SWORD = 2619
    SHIELD_T2 = 2570
    BOW_T3 = 2678
    HP_T1 = 2599
    ARMOR_T13 = 2812
    POISON_T2 = 2725
    SCEPTER_T2 = 2863
    SKULL_T1 = 2731
    SWORD_T1 = 2668
    BOW_T1 = 2677
    SKULL_ST_MEMENTO_F6 = 2525
    EGG = 2729
    SEAL_T1 = 2777
    SKULL_T0 = 2730
    DEF_T2 = 2602
    GL_ESSENCE = 22401
    SUR_T0 = 3155
    ORB_UT_ORN_F6 = 22359
    PRISM_UT_GEM_F7 = 22372
    NODE_HEALTH = 22616
    RING_ENCOUNTER_F4 = 22143
    WAND_T14 = 2496
    ROBE_T15 = 2512
    WAND_T5 = 2566
    ATT_T2 = 2601
    ARMOR_T1 = 2683
    SWORD_T4 = 2670
    LARMOR_T12 = 2704
    LIGHT_GOD_RING_F6 = 21260
    SUR_T2 = 3157
    WAND_ST_WINGED_F5 = 21780
    BOOT_T2 = 2610
    DAG_ST_ETHER_F4 = 8608
    SKULL_T2 = 2732
    SWORD_UT_FANG_F6 = 21137
    BOW_T5 = 2588
    MP_T5 = 2766
    HELM_T6 = 2857
    BOW_T11 = 2701
    ARMOR_T2 = 2575
    VIT_T2 = 2616
    WAND_T0 = 2564
    EPIC_QUEST_CHEST = 3470
    PRISM_T6 = 2851
    WIS_T2 = 2617
    PRISM_T0 = 2787
    DAG_UT_SUNSHINE = 3309
    DAG_T10 = 2697
    PRISM_UT_GHOSTLY_F6 = 3114
    RING_MYST_ENCOUNTER = 22144
    DEX_T2 = 2638
    SEAL_T2 = 2643
    DAGGER_UT_DESTR_F6 = 21092
    ABYSS_KEY = 1802
    BOW_UT_BLOOD_F6 = 21141
    KENDO_STICK = 3141
    SHIELD_T0 = 2568
    SUR_T1 = 3156
    PRISM_T2 = 2845
    DEMON_LORD_RING = 21150
    WAND_UT_FROZEN_F5 = 5138
    KAT_T0 = 3140
    WAND_UT_CONDUCT_F4 = 3123
    STAFF_T1 = 2712
    ROBE_T1 = 2652
    WAND_T1 = 2671
    ROBE_T2 = 2686
    TRAP_T2 = 2739
    SPRITE_WAND_UT = 2635
    HP_T2 = 2604
    SWORD_T12 = 2827
    DEF_T5 = 2760
    SUR_T6 = 3161
    APIARY_ARMOR_UT_F4 = 2297
    MP_T2 = 2605
    WIS_6 = 2983
    STAFF_T11 = 2722
    SUMMER_ROBE_UT_F4 = 8863
    BURNING_RING = 8960
    ORB_T0 = 2788
    SCEPTER_T0 = 2789
    STAFF_T2 = 2713
    ROBE_LIGHT_UT_F3 = 3103
    TRAP_T6 = 2860
    MINI_PRECISION = 22568
    MINI_PROTECTION = 22566
    BOOK_T6 = 2853
    BOW_UT_MORNING_F5 = 8961
    KAT_UT_DOOM_F6 = 21269
    UDL_KEY = 1793
    STAFF_ST_EDICT_F5 = 2524
    RING_ST_INTER_F4 = 2527
    WAND_UT_RISING_F1 = 21151
    BIG_NODESTONE = 21878
    SWORD_UT_ILLU_F6 = 8963
    DAG_T1 = 2581
    WAND_T12 = 2806
    DAG_T2 = 2674
    SWORD_T2 = 2669

    @staticmethod
    def get(value):
        try:
            return ITEM(value)
        except Exception:
            return value

I = ITEM

SKULLS = {
    I.SKULL_CHOCO: {'type': 'dmg'},
    I.SKULL_TORMENT: {'type': 'hp'},
}

SKILL = [I.SKULL_CHOCO, I.SKULL_TORMENT]
LOOT = [I.ATT,]
AUTOUSE = [I.POTION_CRATE, I.ITEM_CRATE, I.VIT, I.WIS, I.DEF, I.GREEN_CRATE, I.MANA_POTION,
           I.VIT_2X,
           I.SPD,
           I.ATT, I.DEX,  # comment for loot
           I.HP_POTION, I.ALCHEM, I.MAGN_RECEIPT, I.ANT_POTION, I.RIGGED_ALCHEMIST, I.MYST_COIN,
           I.MYST_COIN_3,
           I.FUEL_PUMP, I.FUEL_CART, I.LUCKY_BOX, I.EGG]
AUTOPICKUP = [I.SPD, I.ATT, I.MANA, I.HP, I.DEX, I.SPECIAL_CRATE, I.SKULL_CHOCO, I.SKULL_TORMENT,
              # I.BACKPACK, 
              I.CHAR_UNLOCKER, I.CHEST_UNLOCKER, I.QUEST_CHEST, I.ECOIN1,
              I.HP_T6, I.DEX_2X, I.HP_2X, I.ATT_2X, I.INC_RING,
              I.STAFF_T14, I.ROBE_INCUMB_F5, I.LUCKY_KEY, I.STAFF_ST_FIRE_F5,
              I.FIRE_SWORD, I.GL_ESSENCE,
              I.WAND_T14, I.ROBE_T15, I.ARMOR_T15,
              I.WAND_ST_WINGED_F5, I.LIGHT_GOD_RING_F6,
              I.HELM_T6, I.EPIC_QUEST_CHEST, I.PRISM_T6,
              I.RING_MYST_ENCOUNTER, I.ABYSS_KEY, I.WIS_6,
              I.BOOK_T6, I.UDL_KEY,
              I.SWORD_UT_ILLU_F6,
              ]
AUTOUSE_ON_FULL = [I.SPD, I.ATT, I.MANA, I.HP, I.DEX, I.CHAR_UNLOCKER, I.CHEST_UNLOCKER,
                   I.SPECIAL_CRATE]
WARN = []
IMPORTANT = [I.FLAME_IN_BOTTLE, I.SKULL_CHOCO, I.SPECIAL_CRATE, I.GREEN_CRATE, I.HP_T6,
             I.STAFF_ST_FIRE_F5]
