import unicodedata

from shaperglot.checks.no_orphaned_marks import NoOrphanedMarksCheck
from shaperglot.checks.shaping_differs import ShapingDiffersCheck
from shaperglot.checks.unencoded_variants import UnencodedVariantsCheck

isoconv = {
    "aar": "aa",
    "afr": "af",
    "aka": "ak",
    "amh": "am",
    "bam": "bm",
    "ewe": "ee",
    "ful": "ff",
    "hau": "ha",
    "her": "hz",
    "ibo": "ig",
    "kik": "ki",
    "kin": "rw",
    "kon": "kg",
    "kua": "kj",
    "lin": "ln",
    "lub": "lu",
    "lug": "lg",
    "mlg": "mg",
    "nbl": "nr",
    "nde": "nd",
    "ndo": "ng",
    "nya": "ny",
    "orm": "om",
    "run": "rn",
    "sag": "sg",
    "sna": "sn",
    "som": "so",
    "sot": "st",
    "ssw": "ss",
    "swa": "sw",
    "tir": "ti",
    "tsn": "tn",
    "tso": "ts",
    "twi": "tw",
    "ven": "ve",
    "wol": "wo",
    "xho": "xh",
    "yor": "yo",
}

afr_tags = [
    "aaa", "aab", "aal", "aao", "aar", "aas", "aba", "abb", "abi",
    "abm", "abn", "abo", "abr", "abu", "acb", "acd", "ach", "acp",
    "acq", "acw", "acx", "acz", "ada", "add", "ade", "adh", "adj",
    "adq", "adu", "aeb", "aec", "ael", "afb", "afe", "afn", "afo",
    "afr", "aft", "afu", "agb", "agc", "agh", "agj", "agq", "ags",
    "aha", "ahg", "ahi", "ahl", "ahm", "ahn", "ahp", "ahs", "aik",
    "aiw", "aiy", "aja", "ajg", "aju", "ajw", "aka", "akd", "akf",
    "akp", "aks", "aku", "akw", "ala", "ald", "alf", "alw", "alz",
    "amb", "amf", "amh", "amj", "amo", "anc", "anf", "ank", "ann",
    "anu", "anv", "anw", "any", "apd", "aqd", "aqg", "arb", "arq",
    "arv", "ary", "arz", "asa", "asg", "asj", "ass", "asv", "atg",
    "ati", "ato", "atu", "aug", "auh", "auj", "aum", "avi", "avn",
    "avu", "awc", "awn", "awo", "axk", "ayb", "aye", "ayg", "ayi",
    "ayk", "ayl", "ayu", "azo", "bab", "baf", "bag", "bam", "bas",
    "bau", "bav", "baw", "bax", "bba", "bbe", "bbg", "bbi", "bbj",
    "bbk", "bbm", "bbo", "bbp", "bbq", "bbs", "bbt", "bbu", "bbw",
    "bbx", "bby", "bcb", "bce", "bcg", "bci", "bcn", "bcp", "bcq",
    "bcs", "bct", "bcv", "bcw", "bcy", "bcz", "bda", "bde", "bdh",
    "bdi", "bdj", "bdm", "bdn", "bdo", "bdp", "bds", "bdt", "bdu",
    "beb", "bec", "beh", "bej", "bem", "beq", "bes", "bet", "bev",
    "bex", "bez", "bfa", "bfd", "bff", "bfj", "bfl", "bfm", "bfo",
    "bfp", "bga", "bgf", "bgj", "bgo", "bgu", "bhs", "bhy", "bib",
    "bid", "bif", "bij", "bil", "bim", "bin", "bip", "biv", "biw",
    "biz", "bja", "bjg", "bji", "bjo", "bjt", "bju", "bjv", "bjw",
    "bka", "bkc", "bkf", "bkg", "bkh", "bkj", "bkm", "bko", "bkp",
    "bkt", "bkv", "bkw", "bky", "ble", "blh", "bli", "blm", "blo",
    "blv", "bly", "bma", "bmb", "bmd", "bme", "bmf", "bmg", "bmi",
    "bml", "bmo", "bmq", "bms", "bmv", "bmw", "bng", "bni", "bnl",
    "bnm", "bnx", "bnz", "bob", "boe", "bof", "boh", "bok", "bol",
    "bom", "boo", "bot", "bou", "bov", "box", "boy", "boz", "bpd",
    "bpj", "bqa", "bqc", "bqd", "bqf", "bqg", "bqj", "bqk", "bqm",
    "bqo", "bqp", "bqt", "bqu", "bqv", "bqw", "bqx", "bqz", "brf",
    "bri", "brk", "brl", "brm", "brt", "bsc", "bse", "bsf", "bsi",
    "bsj", "bsl", "bso", "bsp", "bsq", "bsr", "bss", "bst", "bsv",
    "bsw", "bsx", "bta", "btc", "bte", "btf", "btg", "btt", "btu",
    "bub", "bud", "buf", "bui", "buj", "bum", "bun", "bus", "buu",
    "buw", "bux", "buy", "buz", "bva", "bvb", "bvf", "bvg", "bvh",
    "bvi", "bvj", "bvm", "bvo", "bvq", "bvw", "bvx", "bwc", "bwg",
    "bwh", "bwj", "bwl", "bwo", "bwq", "bwr", "bws", "bwt", "bwu",
    "bww", "bwy", "bwz", "bxb", "bxc", "bxe", "bxg", "bxk", "bxl",
    "bxp", "bxq", "bxs", "bxv", "bxw", "byb", "byc", "byf", "byg",
    "byi", "byj", "byn", "byp", "bys", "byt", "byv", "bza", "bze",
    "bzm", "bzo", "bzv", "bzw", "bzx", "bzy", "bzz", "cae", "cbj",
    "cbo", "cbq", "cce", "ccg", "cch", "ccj", "cdr", "cen", "cet",
    "cfa", "cfd", "cfg", "cgg", "chw", "cib", "cie", "cjk", "ckl",
    "cko", "ckq", "ckx", "cky", "cla", "cli", "cll", "cme", "cmt",
    "cnu", "coh", "cop", "cou", "cpn", "cpo", "cra", "cry", "csk",
    "cug", "cuh", "cuv", "cwa", "cwb", "cwe", "cwt", "daa", "dae",
    "dag", "dai", "daj", "dal", "dam", "das", "dau", "dav", "dba",
    "dbb", "dbd", "dbg", "dbi", "dbm", "dbo", "dbp", "dbq", "dbr",
    "dbt", "dbu", "dbv", "dbw", "ddd", "dde", "ddn", "dds", "dec",
    "dee", "deg", "dek", "deq", "dez", "dga", "dgb", "dgd", "dgh",
    "dgi", "dgk", "dgl", "dgs", "dhm", "dhs", "dib", "dic", "did",
    "dig", "dii", "dik", "dil", "dim", "dio", "dip", "dir", "diu",
    "diw", "diz", "djc", "dje", "djm", "dks", "dkx", "dlk", "dma",
    "dmb", "dme", "dmm", "dmo", "dmx", "dne", "dnj", "dnn", "dno",
    "doe", "doh", "doo", "dop", "dos", "dot", "dov", "dow", "dox",
    "doy", "doz", "drb", "dri", "drs", "dsh", "dsi", "dsq", "dti",
    "dtk", "dtm", "dtn", "dto", "dts", "dtt", "dtu", "dua", "dug",
    "dur", "dux", "duz", "dwa", "dwr", "dya", "dyi", "dym", "dyo",
    "dyu", "dza", "dzg", "dzn", "ebg", "ebo", "ebr", "ebu", "efa",
    "efe", "efi", "ega", "ego", "ehu", "eja", "eka", "eke", "eki",
    "ekm", "eko", "ekp", "ekr", "elh", "eli", "elm", "elo", "ema",
    "emk", "emn", "enb", "enn", "env", "enw", "eot", "epi", "erh",
    "etb", "eto", "ets", "etu", "etx", "evh", "ewe", "ewo", "eyo",
    "eza", "eze", "fah", "fak", "fal", "fam", "fan", "fap", "fer",
    "ffm", "fgr", "fia", "fie", "fip", "fir", "fkk", "fli", "fll",
    "flr", "fmp", "fni", "fod", "fom", "fon", "fub", "fuc", "fue",
    "fuf", "fuh", "fui", "fuj", "fum", "fuq", "fuu", "fuv", "fvr",
    "fwe", "gaa", "gab", "gax", "gaz", "gbg", "gbh", "gbn", "gbo",
    "gbp", "gbq", "gbr", "gbs", "gbv", "gbx", "gby", "gde", "gdf",
    "gdi", "gdk", "gdl", "gdm", "gdu", "gea", "gec", "ged", "geg",
    "gej", "gek", "gel", "geq", "gev", "gew", "gex", "gey", "gez",
    "ggb", "ggu", "gha", "ghl", "gho", "gic", "gid", "gie", "gis",
    "gix", "giz", "gji", "gjn", "gke", "gkn", "gkp", "gku", "glc",
    "glj", "glo", "glr", "glu", "glw", "gly", "gmd", "gmm", "gmn",
    "gmv", "gmx", "gmz", "gna", "gnd", "gne", "gng", "gnh", "gnj",
    "gnk", "gnz", "goa", "god", "gof", "gog", "gol", "gou", "gow",
    "gox", "goy", "gpa", "gqa", "gqr", "grd", "grh", "grj", "grr",
    "gru", "grv", "gry", "gsl", "gso", "gua", "gud", "guk", "gur",
    "guw", "gux", "guz", "gvl", "gvm", "gwa", "gwb", "gwd", "gwe",
    "gwg", "gwj", "gwn", "gwr", "gwx", "gxx", "gya", "gye", "gyg",
    "gyi", "gyl", "gza", "hae", "hag", "han", "haq", "har", "hau",
    "hav", "hay", "hba", "hbb", "hbn", "hdy", "hed", "heh", "hem",
    "her", "hgm", "hhr", "hia", "hig", "hij", "hio", "hka", "hke",
    "hmb", "hna", "hnh", "hod", "hoe", "hol", "hom", "hoo", "hor",
    "hoz", "hts", "huc", "hum", "hwa", "hwo", "hya", "ibb", "ibe",
    "ibm", "ibn", "ibo", "ibr", "iby", "ica", "ich", "ida", "idc",
    "idd", "ide", "idr", "ids", "idu", "ife", "ifm", "igb", "ige",
    "igl", "igw", "ihi", "ijc", "ije", "ijj", "ijn", "ijs", "iki",
    "ikk", "ikl", "iko", "ikp", "ikv", "ikw", "ikx", "ikz", "ilb",
    "ilv", "ior", "iqw", "iri", "irk", "ish", "isi", "isn", "iso",
    "isu", "itm", "its", "itw", "iya", "iyo", "iyx", "izr", "izz",
    "jab", "jad", "jaf", "jbe", "jbn", "jbu", "jek", "jen", "jer",
    "jeu", "jgb", "jgk", "jgo", "jia", "jib", "jid", "jie", "jii",
    "jim", "jit", "jjr", "jku", "jle", "jmb", "jmc", "jmi", "jmr",
    "jms", "jni", "jnj", "job", "jod", "jow", "jrr", "jrt", "jub",
    "jud", "juh", "juk", "jum", "juo", "juu", "juw", "jwi", "jyy",
    "kab", "kad", "kah", "kai", "kaj", "kam", "kao", "kbj", "kbl",
    "kbn", "kbo", "kbp", "kbr", "kbs", "kby", "kbz", "kcc", "kce",
    "kcf", "kcg", "kch", "kci", "kcj", "kck", "kcm", "kcp", "kcq",
    "kcr", "kcs", "kcu", "kcv", "kcw", "kcx", "kcy", "kcz", "kdc",
    "kde", "kdg", "kdh", "kdi", "kdj", "kdl", "kdm", "kdn", "kdp",
    "kdu", "kdx", "kdz", "keb", "kec", "ked", "kef", "keg", "kel",
    "ken", "keo", "ker", "kes", "keu", "kez", "kfl", "kfn", "kfo",
    "kfz", "kga", "kgo", "kgt", "khj", "khq", "khu", "khx", "khy",
    "kia", "kib", "kid", "kie", "kik", "kil", "kin", "kiv", "kiz",
    "kka", "kkd", "kke", "kki", "kkj", "kkm", "kko", "kkq", "kkr",
    "kks", "kku", "kkw", "klc", "klf", "klk", "klo", "klu", "kma",
    "kmb", "kme", "kmi", "kmp", "kmq", "kmw", "kmy", "kna", "knc",
    "knf", "kng", "kni", "knk", "kno", "knp", "knu", "knw", "kny",
    "knz", "koc", "koe", "kof", "koh", "kon", "koo", "koq", "kot",
    "kou", "kov", "kow", "kpa", "kph", "kpk", "kpl", "kpo", "kpz",
    "kqg", "kqh", "kqk", "kqm", "kqn", "kqo", "kqp", "kqs", "kqu",
    "kqx", "kqy", "kqz", "krh", "krn", "krp", "krs", "krt", "krw",
    "krx", "ksa", "ksb", "ksf", "ksm", "kso", "ksp", "ksq", "kss",
    "kst", "ksv", "ktb", "ktc", "ktf", "kth", "ktj", "kty", "ktz",
    "kua", "kub", "kug", "kuh", "kuj", "kul", "kun", "kus", "kuw",
    "kvf", "kvi", "kvj", "kvm", "kwb", "kwc", "kwg", "kwl", "kwm",
    "kwn", "kwp", "kws", "kwu", "kwv", "kwy", "kwz", "kxb", "kxc",
    "kxh", "kxj", "kxx", "kya", "kye", "kyf", "kym", "kyq", "kza",
    "kzc", "kzn", "kzo", "kzr", "kzy", "laf", "lag", "lai", "laj",
    "lak", "lal", "lam", "lan", "lap", "lar", "las", "lbi", "lch",
    "lda", "ldb", "ldd", "ldg", "ldh", "ldi", "ldj", "ldk", "ldl",
    "ldm", "ldo", "ldp", "ldq", "lea", "leb", "led", "lee", "lef",
    "leh", "lej", "lel", "lem", "leo", "les", "lfa", "lgg", "lgm",
    "lgn", "lgq", "lgz", "lia", "lie", "lig", "lik", "lin", "lip",
    "liq", "liu", "liy", "liz", "lkb", "lke", "lko", "lkr", "lks",
    "lky", "lla", "llb", "llc", "lli", "lln", "lma", "lmd", "lme",
    "lmi", "lmp", "lmx", "lna", "lnb", "lnl", "lno", "lns", "lnu",
    "lnz", "lob", "lof", "log", "loh", "loi", "lok", "lol", "lom",
    "lon", "loo", "lop", "loq", "lor", "lot", "loz", "lpx", "lri",
    "lrm", "lro", "lse", "lsm", "lth", "lto", "lts", "lua", "lub",
    "luc", "lue", "lug", "luj", "lul", "lum", "lun", "luo", "lup",
    "luq", "luw", "lwa", "lwg", "lwo", "lyn", "mae", "maf", "mas",
    "maw", "mbm", "mbo", "mbu", "mbv", "mcj", "mck", "mcn", "mcp",
    "mcs", "mct", "mcu", "mcw", "mcx", "mda", "mdd", "mde", "mdg",
    "mdi", "mdj", "mdk", "mdm", "mdn", "mdp", "mdq", "mdt", "mdu",
    "mdw", "mdx", "mdy", "mea", "mei", "men", "meq", "mer", "mes",
    "mev", "mew", "mey", "mfc", "mfd", "mff", "mfg", "mfh", "mfi",
    "mfj", "mfk", "mfl", "mfm", "mfn", "mfo", "mfq", "mfu", "mfv",
    "mfx", "mfz", "mgb", "mgc", "mgd", "mge", "mgg", "mgh", "mgi",
    "mgj", "mgn", "mgo", "mgq", "mgr", "mgs", "mgv", "mgw", "mgy",
    "mgz", "mhb", "mhd", "mhi", "mhk", "mhm", "mho", "mhw", "mif",
    "mij", "mje", "mjh", "mjs", "mka", "mkf", "mkk", "mkl", "mko",
    "mku", "mlb", "mlg", "mlj", "mlk", "mlo", "mlq", "mlr", "mls",
    "mlt", "mlw", "mma", "mmf", "mmu", "mmy", "mmz", "mne", "mnf",
    "mnh", "mnk", "mny", "moa", "moi", "moj", "mor", "mos", "mou",
    "mow", "moy", "moz", "mpa", "mpe", "mpg", "mpi", "mpk", "mqb",
    "mql", "mqu", "mrt", "mru", "msc", "mse", "msj", "msv", "msw",
    "mtb", "mtk", "mtl", "mua", "mub", "muc", "mug", "muh", "muj",
    "muo", "mur", "muu", "muy", "muz", "mvh", "mvu", "mvw", "mvz",
    "mwe", "mwk", "mwm", "mwn", "mws", "mwu", "mwz", "mxc", "mxf",
    "mxg", "mxh", "mxl", "mxo", "mxu", "mxx", "myb", "myc", "mye",
    "myf", "myg", "myj", "myk", "mym", "myo", "mys", "myx", "mzb",
    "mzd", "mzj", "mzk", "mzm", "mzv", "mzw", "naj", "naq", "nar",
    "nat", "naw", "nba", "nbb", "nbd", "nbh", "nbl", "nbm", "nbo",
    "nbp", "nbr", "nbv", "nbw", "ncr", "ncu", "nda", "ndb", "ndc",
    "ndd", "nde", "ndg", "ndh", "ndi", "ndj", "ndk", "ndl", "ndm",
    "ndn", "ndo", "ndp", "ndq", "ndr", "ndt", "ndu", "ndv", "ndw",
    "ndy", "ndz", "neb", "ned", "ney", "nfd", "nfr", "nfu", "nga",
    "ngb", "ngc", "ngd", "nge", "ngg", "ngh", "ngi", "ngj", "ngl",
    "ngn", "ngo", "ngp", "ngq", "ngs", "ngv", "ngw", "ngx", "ngy",
    "ngz", "nhb", "nhr", "nhu", "nie", "nih", "nim", "nin", "niq",
    "nix", "niy", "nja", "njd", "njj", "njl", "njr", "njx", "njy",
    "nka", "nkc", "nkn", "nko", "nkq", "nkt", "nku", "nkv", "nkw",
    "nkx", "nkz", "nla", "nle", "nlj", "nlo", "nlu", "nmc", "nmd",
    "nmg", "nmi", "nmj", "nml", "nmn", "nmq", "nmr", "nmz", "nnb",
    "nnc", "nne", "nnh", "nnj", "nnn", "nnq", "nnu", "nnw", "nnz",
    "noq", "now", "noy", "noz", "nqg", "nqk", "nql", "nqo", "nra",
    "nrb", "nsc", "nse", "nsg", "nsh", "nso", "nsx", "nte", "nti",
    "ntk", "ntm", "nto", "ntr", "nue", "nuh", "nui", "nuj", "nup",
    "nus", "nuu", "nuv", "nvo", "nwb", "nwe", "nwm", "nxd", "nxi",
    "nxo", "nya", "nyb", "nyc", "nyd", "nye", "nyf", "nyg", "nyi",
    "nyj", "nyk", "nym", "nyn", "nyo", "nyp", "nyr", "nyu", "nyy",
    "nza", "nzb", "nzd", "nzi", "nzk", "nzu", "nzy", "nzz", "obl",
    "obu", "oda", "odu", "ofu", "ogb", "ogc", "ogg", "ogo", "ogu",
    "okb", "okd", "oke", "oki", "okr", "oks", "oku", "okx", "old",
    "olm", "olu", "omi", "oml", "omt", "opa", "orc", "org", "orm",
    "orr", "orx", "oso", "ost", "otr", "oua", "oub", "oyd", "ozm",
    "pae", "pai", "pbi", "pbl", "pbn", "pbo", "pbp", "pbr", "pcn",
    "pcw", "pem", "pfe", "pgs", "phm", "pic", "pil", "pip", "piw",
    "piy", "pkb", "pko", "plj", "plr", "pmb", "pmm", "pmn", "pnd",
    "png", "pnl", "pnq", "pny", "pnz", "pof", "poy", "ppp", "pqa",
    "pug", "puu", "pwb", "pye", "pym", "rag", "ras", "rax", "reg",
    "rel", "rer", "res", "rif", "rim", "rin", "rkm", "rnd", "rng",
    "rnw", "rod", "rof", "rou", "rub", "ruc", "ruf", "rui", "ruk",
    "run", "ruy", "ruz", "rwk", "rwm", "rzh", "saa", "sad", "saf",
    "sag", "sak", "saq", "sav", "say", "sba", "sbd", "sbf", "sbj",
    "sbk", "sbm", "sbp", "sbs", "sbw", "sby", "sbz", "scv", "scw",
    "sde", "sdj", "sds", "seb", "sef", "seg", "seh", "sen", "sep",
    "seq", "ses", "sev", "sfw", "sgc", "sgi", "sgm", "sgw", "sha",
    "shc", "she", "shg", "shi", "shj", "shk", "sho", "shq", "shr",
    "shu", "shw", "shy", "shz", "sid", "sie", "sif", "sig", "sil",
    "sir", "siz", "sjg", "sjs", "skq", "skt", "sld", "slx", "smd",
    "smx", "sna", "snf", "sng", "snk", "snm", "snq", "snw", "soc",
    "sod", "soe", "soh", "sok", "som", "soo", "sop", "sor", "sos",
    "sot", "sox", "soy", "soz", "spp", "spy", "sqa", "sqh", "sqm",
    "srr", "ssc", "ssl", "ssn", "ssw", "ssy", "stj", "stv", "sub",
    "suj", "suk", "suq", "sur", "sus", "suw", "swa", "swb", "swc",
    "swf", "swh", "swj", "swk", "swn", "swq", "swy", "sxb", "sxe",
    "sxs", "sxw", "syc", "syi", "syk", "sym", "sys", "syx", "sze",
    "szg", "szv", "tag", "tak", "tal", "tan", "tap", "taq", "tax",
    "taz", "tbi", "tbm", "tbr", "tbt", "tbz", "tcc", "tcd", "tck",
    "tda", "tde", "tdk", "tdl", "tdo", "tdq", "tdv", "tec", "ted",
    "teg", "tek", "tem", "teo", "teq", "teu", "tex", "tey", "tez",
    "tfi", "tga", "tgd", "tgw", "tgy", "thk", "thu", "thv", "thy",
    "thz", "tia", "tic", "tig", "tii", "tik", "tiq", "tir", "tiv",
    "tja", "tjn", "tjo", "tke", "tkq", "tlj", "tll", "tlo", "tma",
    "tmc", "tms", "tmv", "tng", "tnr", "tny", "tod", "tog", "toh",
    "toi", "toq", "tor", "toz", "tpm", "tqq", "tqr", "trj", "tsa",
    "tsb", "tsc", "tsh", "tsn", "tso", "tsp", "tst", "tsv", "tsw",
    "ttb", "ttf", "ttj", "ttl", "ttq", "ttr", "tug", "tui", "tul",
    "tum", "tuq", "tuv", "tuy", "tuz", "tvd", "tvs", "tvu", "twi",
    "twl", "twn", "two", "twq", "twx", "txj", "tye", "tyi", "tyu",
    "tyx", "tzm", "uba", "ubi", "uda", "udl", "udu", "uha", "uiv",
    "uji", "ukh", "ukp", "ukq", "uku", "ukw", "ula", "ulb", "umb",
    "umm", "une", "urh", "usk", "uss", "uta", "uth", "utr", "uya",
    "vae", "vag", "vai", "vaj", "vau", "vem", "ven", "ver", "vid",
    "vif", "vig", "vin", "vit", "vki", "vkj", "vmk", "vmr", "vmw",
    "vor", "vum", "vun", "vut", "wal", "wan", "wav", "wbf", "wbh",
    "wbi", "wbj", "wci", "wdd", "wec", "weh", "wem", "wib", "wja",
    "wji", "wka", "wlc", "wle", "wll", "wlx", "wma", "wmw", "wni",
    "wob", "wof", "wok", "wol", "wom", "won", "woy", "wrn", "wss",
    "wti", "wud", "wum", "wun", "wwa", "www", "xab", "xam", "xan",
    "xdo", "xed", "xeg", "xel", "xho", "xii", "xkb", "xkg", "xkt",
    "xku", "xkv", "xma", "xmb", "xmc", "xmd", "xmg", "xmj", "xnz",
    "xoc", "xog", "xom", "xon", "xpe", "xrb", "xsh", "xsj", "xsm",
    "xsn", "xsq", "xtc", "xuo", "xuu", "xwe", "xwg", "xwl", "yaf",
    "yaj", "yal", "yam", "yao", "yas", "yat", "yav", "yax", "yay",
    "yaz", "yba", "ybb", "ybj", "ybl", "yei", "yel", "yer", "yes",
    "yey", "yko", "yky", "ymg", "ymk", "ymm", "yng", "ynq", "yns",
    "yom", "yor", "yot", "yre", "yul", "yun", "zag", "zah", "zaj",
    "zak", "zay", "zaz", "zdj", "zen", "zga", "zgh", "zhi", "zhw",
    "zil", "zim", "zin", "zir", "ziw", "ziz", "zmb", "zmf", "zmn",
    "zmo", "zmp", "zmq", "zms", "zmw", "zmx", "zmz", "zna", "zne",
    "zns", "zrn", "zua", "zul", "zuy", "zwa"
]

unencoded_variants = {
    "tod_Latn": ["ʋ", "Ʋ"],
    "xpe_Latn": ["Ɓ"],
    "lom_Latn": ["Ɓ"],
    "dnj_Latn": ["Ɓ"],
    "gaa_Latn": ["Ʃ", "Ʒ"],
}

available_languages = {
    isoconv.get(tag, tag)+"_Latn": tag for tag in afr_tags
}

class AfricanLatinProvider:
    @classmethod
    def fill(cls, language):
        if language["script"] != "Latn":
            return
        if language["id"] not in available_languages:
            return

        exemplar_chars = language.get("exemplarChars", {})
        bases = exemplar_chars.get("base", "").split() or []
        auxiliary = exemplar_chars.get("auxiliary", "").split() or []

        language["shaperglot_checks"].extend(
            cls.build_no_orphaned_marks(bases, auxiliary)
        )
        language["shaperglot_checks"].extend(
            cls.build_unencoded_variants(language, bases, auxiliary)
        )
        language["shaperglot_checks"].extend(
            cls.build_sd_smcp(bases, auxiliary)
        )

    @classmethod
    def build_no_orphaned_marks(cls, bases, auxiliary):
        basemarks = []
        for base in bases:
            if len(base) > 1:
                unpack = base.replace("{", "").replace("}", "")
                for char in unpack:
                    if unicodedata.combining(char):
                        basemarks.append(unpack)
        for aux in auxiliary:
            if len(aux) > 1:
                unpack = aux.replace("{", "").replace("}", "")
                for char in unpack:
                    if unicodedata.combining(char):
                        basemarks.append(unpack)
        basemark_string = "".join(basemarks)
        if not basemark_string:
            return
        yield NoOrphanedMarksCheck(
            {
                "check": "no_orphaned_marks",
                "input": {"text": basemark_string}
            }
        )
        yield NoOrphanedMarksCheck(
            {
                "check": "no_orphaned_marks",
                "input": {"text": basemark_string, "features": {"smcp": True}},
                "conditions": {"features": ['smcp']},
            }
        )

    @classmethod
    def build_unencoded_variants(cls, language, bases, auxiliary):
        if "Ŋ" in bases or 'Ŋ' in auxiliary:
            yield UnencodedVariantsCheck({
                "check": "unencoded_variants",
                "input": {"text": 'Ŋ'}
            })
        for char in unencoded_variants.get(language["id"], []):
            yield UnencodedVariantsCheck({
                "check": "unencoded_variants",
                "input": {"text": char}
            })

    @classmethod
    def build_sd_smcp(cls, bases, auxiliary):
        for letter in bases + auxiliary:
            if len(letter) == 1 and unicodedata.category(letter) == 'Ll':
                yield ShapingDiffersCheck({
                    'check': 'shaping_differs',
                    'inputs': [{'text': letter}, {'text': letter, 'features': {'smcp': True}}],
                    'conditions': {'features': ['smcp']},
                    'rationale': "Requires Small-cap: " + letter,
                })
