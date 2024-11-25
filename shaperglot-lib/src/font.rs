use skrifa::{
    raw::{
        tables::post::{PString, DEFAULT_GLYPH_NAMES},
        types::Version16Dot16,
        ReadError, TableProvider,
    },
    FontRef,
};

pub(crate) fn glyph_names(font: &FontRef) -> Result<Vec<String>, ReadError> {
    #[allow(clippy::unwrap_used)] // Heck, Skrifa does the same
    let glyph_count = font.maxp().unwrap().num_glyphs().into();
    let mut names = Vec::with_capacity(glyph_count);
    if let Ok(post) = font.post() {
        match post.version() {
            Version16Dot16::VERSION_1_0 => {
                names.extend(DEFAULT_GLYPH_NAMES.into_iter().map(|x| x.to_string()));
            }
            Version16Dot16::VERSION_2_0 => {
                if let Some(data) = post.string_data() {
                    let strings: Vec<Option<PString>> = data.iter().map(|x| x.ok()).collect();
                    if let Some(index) = post.glyph_name_index() {
                        names.extend(
                            (0..glyph_count)
                                .map(|gid| {
                                    (
                                        gid,
                                        index.get(gid).and_then(|idx| {
                                            let idx = idx.get() as usize;
                                            if idx < 258 {
                                                Some(DEFAULT_GLYPH_NAMES[idx].to_string())
                                            } else {
                                                let entry = strings.get(idx - 258)?;
                                                entry.map(|x| x.to_string())
                                            }
                                        }),
                                    )
                                })
                                .map(|(gid, maybe_name)| {
                                    maybe_name.unwrap_or_else(|| format!("gid{}", gid))
                                }),
                        );
                    }
                }
            }
            _ => {}
        }
    }
    if names.len() < glyph_count {
        names.extend((names.len()..glyph_count).map(|gid| format!("gid{}", gid)));
    }
    Ok(names)
}
