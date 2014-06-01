set nocompatible              " be iMproved, required
filetype off                  " required
set t_Co=256

" Vundle
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

Bundle 'xoria256.vim'
Bundle 'Lokaltog/powerline', {'rtp': 'powerline/bindings/vim/'}
Bundle 'kien/ctrlp.vim'
Bundle 'scrooloose/nerdtree'

call vundle#end()            " required
filetype plugin indent on    " required

colorscheme xoria256
set guifont=menlo\ for\ powerline:h16
set guioptions-=T 		" Removes top toolbar
set guioptions-=r 		" Removes right hand scroll bar
set go-=L 				" Removes left hand scroll bar
set linespace=15
set number 				" always show line numbers
syntax on

set tabstop=4           " a tab is four spaces
set smarttab
set autoindent          " always set autoindenting on
set copyindent          " copy the previous indentation on autoindenting
set tags=tags
set softtabstop=4       " when hitting <BS>, pretend like a tab is removed, even if spaces
set expandtab           " expand tabs by default (overloadable per file type later)
set shiftwidth=4        " number of spaces to use for autoindenting
set shiftround          " use multiple of shiftwidth when indenting with '<' and '>'
set smartcase           " ignore case if search pattern is all lowercase,
set autowrite  			" save on buffer switch
set mouse=a 			" mouse support

" Powerline (Fancy thingy at bottom stuff)
let g:Powerline_symbols = 'fancy'
set laststatus=2   		" Always show the statusline
set encoding=utf-8 		" Necessary to show Unicode glyphs
set noshowmode	 		" Hide the default mode text (e.g. -- INSERT -- below the statusline)

" Nerdtree (tree view on the side)
nmap <C-b> :NERDTreeToggle<cr>

" CtrlP
map <D-p> :CtrlP<cr>
map <C-r> :CtrlPBufTag<cr>
set wildignore+=*/vendor/**	" vendor exclude for laravel

" Splitting
nmap :sp :rightbelow sp<cr> " create split below
nmap vs :vsplit<cr>
nmap sp :split<cr>
nmap <C-h> <C-w>h 		" easier window navigation
nmap <C-j> <C-w>j
nmap <C-k> <C-w>k
nmap <C-l> <C-w>l
nmap :bp :BufSurfBack<cr> " quickly go forward or backward to buffer
nmap :bn :BufSurfForward<cr>
