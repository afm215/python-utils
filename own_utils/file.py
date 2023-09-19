__package__="own_utils"

import tarfile
from .basics import format_number
from .paths import flatten_paths_recursively, format_prepath
from .bash_command import run
import os
import time 
import uuid
from tqdm import tqdm

def extract_file_lines_to_list(file_path:str, skip_blank_line=True):
    """
    Extract each lines of a file into a list and ignore \n

    INPUTS:
    -------
        - file path : the path of the file to be considered
        - skip_blank_line : if set to True, remove the blank lines
    """
    file = open(file_path, 'r')
    raw_lines = file.readlines() 
    result = ''.join(raw_lines).split('\n')
    if skip_blank_line:
        result = list(filter(lambda elt: elt!='', result))
    return result

def compress_to_tar(target = './', file_tree_level=0,replace_existing = False, remove_init_folder = False,  run_with_bash = True):
    """
    add target to tar file named "<target_name>.tar

    INPUTS: 
    ------
        - target
        - file_tree_level : default is 0 i.e. creat a tar archive of the target. If set to a number k, will convert the content at depth k in tar
        - replace_existing : if set to False, skip th ewriting if the tar file already exists
        - remove_init_folder : if True, remove the original folder after taring
        - run_with_bash : if True, use the bash command instead of the python tarfile lib
    """
    print("getting files path to tar ... ", flush=True)
    content_to_tar_paths = flatten_paths_recursively(
        target, depth=file_tree_level, output_absolute_path=True
                            ) if file_tree_level > 1 else (
                                    list(
                                        map(
                                        lambda elt :format_prepath(target) +  elt, os.listdir(target)
                                        )
                                    ) if file_tree_level == 1 else [target] )

    content_to_tar_paths = list(filter(lambda elt : elt[-3:]!= 'tar', content_to_tar_paths))
    length = len(content_to_tar_paths)
    print("creating the tars for ", length, " elements", flush=True)
    for (i,elt_path) in enumerate(content_to_tar_paths):
        print("Completed at ", format_number(i / length, max_decimal_length=2),  end = '\r', flush=True)
        if replace_existing or not(os.path.exists(elt_path + '.tar')):
            try:
                os.remove(elt_path + '.tar')
            except :
                pass
            if(run_with_bash):
                path_split =  list(filter(lambda elt: elt != "", elt_path.split('/')))
                if path_split[-1] == '':
                    path_split =  path_split[:-1] # remove the empty elt that corresponds to the last '/'
                elt_parent_path = '/'.join(path_split[:-1]) if len(path_split) > 1 else "./"
                if elt_path[0]=="/":
                    elt_parent_path = "/" + elt_parent_path
                elt_name = path_split[-1]
                cmd = "tar -cf " + elt_path + ".tar "+ "-C "+ elt_parent_path + " " + elt_name
                run(cmd, False, False)
            else:
                with tarfile.open(elt_path+ '.tar', "w") as tf:
                    arcname = elt_path.split('/')[-1]
                    tf.add(elt_path, arcname=arcname)
            if remove_init_folder:
                run("rm -r "+ elt_path, False , False)                
        else:
            print("file already existing : ", elt_path+ '.tar', flush=True)
    print(flush=True)

def extracts_tar(path:str = './', remove_init_tar_folder = False, output_folder:str=None):
    """
    Extract the specified tar

    INPUTS:
    -------
    - path : file to ward the tar file
    - remove_init_tar_folder : If set to True, remove the file located at `path`after the extraction
    - output_folder : if None, the extracted content will be at the same level as the input filen, else the content will be deplace in output_folder 
    """
    if os.path.isfile(path):
        path_split = path.split('/')
        if output_folder is None:
            dir_path = '/'.join(path_split[:-1])
        else:
            dir_path = output_folder
            os.makedirs(dir_path, exist_ok=True)
        if path[-3:] == 'tar' :
            cmd = "tar -xf " + path + ' -C ' + dir_path

        elif path[-6:] == '.tar.gz':
            cmd = "tar -xzf " + path + ' -C ' + dir_path
        else:
            return
        try:
            run(cmd, False, False)
        except Exception as e:
            print("error met with ", path, flush=True)
            raise e
        if remove_init_tar_folder:
            run(f"rm {path}", False, False)
    else:
        dir_path = format_prepath(path)
        for elt in os.listdir(dir_path):
            extracts_tar(dir_path + elt, remove_init_tar_folder, output_folder)

def add_sub_tar_to_tar(tar_path:str, output_tar:str, last_file:bool, buffer=None, remove_sub_tar=True):
    if buffer is not None:
        if buffer < 8920:
            buffer = 8920
    if tar_path[-4:] == ".tar":
        assert output_tar[-4:] == ".tar", f"output_tar should have the same extension, found {tar_path} {output_tar}"
        tar_end =b"\x00"
        for i in range(8910):
            tar_end+= b"\x00"
        assert len(tar_end) == 8911
        inter_str = b"\x00"
        for i in range(206):
            inter_str+=b"\x00"
    else:
        raise NotImplementedError(".tar files expected")

    
    tar_to_add = open(tar_path, "rb")
    output = open(output_tar, "ab")
    old_batch = tar_to_add.read(buffer)
    batch = tar_to_add.read(buffer)
    while len(batch) == buffer:
        output.write(old_batch)
        del old_batch
        old_batch = batch
        batch = tar_to_add.read(buffer)
    last_content = old_batch + batch
    assert last_content[-8911:] == tar_end, f"wrong end with {tar_path}"
    if last_file:
        pass
    else:
        last_content = last_content[-8911:] + inter_str

    output.write(last_content)
    output.close()
    tar_to_add.close()
    if remove_sub_tar:
        run(f"rm {tar_path}", False, False)

def concatenate_tar_list(tar_list, output_tar, buffer=None, remove_sub_tar = False):
    for tar_path in tar_list[:-1]:
        print(tar_path)
        add_sub_tar_to_tar(tar_path, output_tar, False, buffer, remove_sub_tar)
    print(tar_list[-1])
    add_sub_tar_to_tar(tar_list[-1], output_tar, True, buffer, remove_sub_tar)


def copy(src_path:str, dst:str, use_rsync: bool =False, recursive = False, archive_mode=False):
    """
    Copy `src_path` to `dst`

    INPUTS:
    -------
    - src_path
    - dst
    - use_rsync: if True will run rsync else , it uses cp
    - recursive : performs recursive copy
    - archive_mode : only with rsync ! use the -a option, not compative with recursive  = True
    """
    dst = format_prepath(dst)
    core = src_path + " " + dst
    tool = "rsync " if use_rsync else "cp " 
    if recursive:
        assert archive_mode == False, "archive mode should not be uses with recursive = True"
        tool += "-r "
    if archive_mode:
        assert use_rsync, "archive mode only available with rsync"
        tool += "-a "
    cmd = tool + core
    run(cmd, False, False)

def move_mapped_files_from_src(folder_to_map, src_folder, output_folder):
    files_to_be_map = flatten_paths_recursively(folder_to_map, False)
    for file_path in tqdm(files_to_be_map):    
        src_path = os.path.join(src_folder, file_path)
        os.makedirs(os.path.join(output_folder, os.path.dirname(file_path)), exist_ok=True)
        dest_path = os.path.join(output_folder, file_path)
        run("rsync -ah {}  {}".format(src_path, dest_path), False, False)       

class MultiProcessCacheHandler():
    ## Class to handle cache shared through several processes
    def create_error_file(self):
        with open (self.error_file, "w"):
            pass
    def check_raised_error(self)->bool:
        try:
            return os.path.exists(self.error_file)
        except FileNotFoundError:
            return False
    
    def check_and_reraise_raised_error(self):
        try:
            if os.path.exists(self.error_file):
                raise Exception(f"error detected {self.error_file}")
        except FileNotFoundError:
            return
    


        
    def __init__(self, cache_dir: str, cache_path: str, process_id: int = 0,nb_process:int = 1,  save_dir: str=None, multithread_save=False, debugging:bool = False):
        """
        INPUT :
        - cache_dir: path of the cache fodler
        - cache_path : a symbolic link will be created within the current folder, and will be used by all processes
        - process_id: if id is zero, the process will handle cache creation and deletion
        - nb_process : nb of process sharing the same cache        
        - save_dir : if not none, will be considered as a default save path for the cache (see add_folder_to_save)
        - multithread_save : use multi process compress into tar of set to True 
        """
        self.debugging = debugging
        self.leader = False
        self.cache_dir = None
        self.multithread_save = multithread_save
        cache_path = os.path.abspath(cache_path) 
        if cache_path[-1] == "/":
            cache_path = cache_path[:-1]
        self.cache_link= cache_path
        self.folder_to_save= []
        self.save_dir = None
        self.root_renaming=None
        if save_dir:
            self.save_dir = os.path.normpath(save_dir) +"/"        
        self.nb_process = nb_process
        self.process_id = process_id
        self.communication_folder = os.path.join(os.path.expanduser('~'), ".cache_handler_communication/" + self.cache_link.replace("/", '-'))
        self.error_file =  os.path.join(self.communication_folder, "ERROR")
        if process_id == 0:
            try:
                self.leader = True
                self.cache_dir = os.path.join(cache_dir,str(uuid.uuid4()))
                os.makedirs(self.cache_dir)
                if os.path.exists(self.cache_link):
                    print(f"link {self.cache_link} exists ")
                assert not(os.path.exists(self.cache_link))
                try:
                    os.makedirs(self.communication_folder)
                except FileExistsError as e:
                    self.create_error_file()
                    raise e
                os.symlink(self.cache_dir, self.cache_link, target_is_directory= True)
                print("symlink created", flush=True)
            except Exception as e:
                self.create_error_file()
                raise e
            

        while not(os.path.exists(self.cache_link)):
            time.sleep(1)
            self.check_and_reraise_raised_error()

        self.cache_link = format_prepath(self.cache_link)
    def add_folder_to_save(self, folder_path:str, dst_path:str=None):
        """
        Will save at save function call, the specified folder within the dst_path as a tar file
        save_function will be call at deletion
        INPUT:
        - folder_path: relative or abs path toward the folder to be saved
        - dst_path : destination folder
        """
        if self.debugging:
            return
        if not(self.leader):
            return
        if not(dst_path):
            dst_path = self.save_dir if self.save_dir else "./"
        cache_path_to_save = folder_path if folder_path[0] == "/" else os.path.join(self.cache_dir, folder_path)
        for i,(cache_path, _) in enumerate(self.folder_to_save):
            if cache_path in cache_path_to_save:
                ## if cache_patrh_to_save is a child of the considered cach path 
                self.folder_to_save = self.folder_to_save[:i] + [[cache_path_to_save, format_prepath(dst_path)]] + self.folder_to_save[i:]
                return
        self.folder_to_save.append([cache_path_to_save, format_prepath(dst_path)])

    def save(self):
        if self.debugging:
            return
        # show that the process is ready
        if self.leader:
            print("waiting for all cache handler to be ready", flush =True)
        if not(self.leader) or not(self.multithread_save):
            with open(os.path.join(self.communication_folder, "READY_" + str(self.process_id)), "w"):
                pass

        if self.multithread_save:
            if self.leader:
                print("saving cache with multi process...", flush = True)
                ## cheating
                with open(os.path.join(self.communication_folder, "folder_to_save"), "w")  as file_cheat:
                    for (src_folder, dst_folder) in self.folder_to_save:
                        file_cheat.write(src_folder + "$" + dst_folder+"\n")
                with open(os.path.join(self.communication_folder, "READY_" + str(self.process_id)), "w"):
                    pass
            while not(os.path.exists(os.path.join(self.communication_folder, "folder_to_save"))) or len(list(filter(lambda elt : elt[:5] == "READY", os.listdir(self.cache_dir)))) != self.nb_process:
                time.sleep(1)
            if self.leader:
                time.sleep(2)
                run("rm {}".format(os.path.join(self.communication_folder, "READY_*")), False, True, True)
            if not(self.leader):
                file_content = extract_file_lines_to_list(os.path.join(self.communication_folder, "folder_to_save"))
                self.folder_to_save = [elt.split("$") for elt in file_content]
                self.cache_dir = os.readlink(self.cache_link)
            for (src_folder, dst_folder) in self.folder_to_save:
                if self.leader:
                    try:
                        file_to_remove_list = list(filter(lambda elt: elt[:22] == "UNHOLDFOLDEREXTRACTION", os.listdir(self.communication_folder)))
                        for file in file_to_remove_list:
                            os.remove(os.path.join(self.communication_folder, file))
                    except Exception:
                        pass
                if os.path.normpath(src_folder) == os.path.normpath(self.cache_dir):
                        os.makedirs(os.path.join(self.cache_dir, self.root_renaming))
                        src_folder = os.path.join(self.cache_dir, self.root_renaming)
                        run("mv {} {}".format(os.path.join(self.cache_dir, "*"), src_folder), False, True, True)
                        # TODO do not do this, pick all the file and create a new folder with the correct name !
                        os.makedirs(os.path.join(self.cache_dir, self.root_renaming))
                        src_folder = os.path.join(self.cache_dir, self.root_renaming)
                        run("mv {} {}".format(os.path.join(self.cache_dir, "*"), src_folder), False, True, True)
                src_folder = src_folder[:-1] if src_folder[-1] == "/" else src_folder
                tar_name  = src_folder + self.process_id + ".tar"
                depth = 1
                elts_to_compress = flatten_paths_recursively(src_folder, depth = depth)
                while len(elts_to_compress) < self.nb_process:
                    depth += 1 
                    elts_to_compress = flatten_paths_recursively(src_folder, depth = depth)
                length = len(elts_to_compress)
                nb_elt_per_process = length // self.nb_process
                if self.process_id == self.nb_process - 1:
                    elts_to_compress = elts_to_compress[self.process_id * nb_elt_per_process:]
                else:
                    elts_to_compress = elts_to_compress[self.process_id * nb_elt_per_process: (self.process_id + 1) * nb_elt_per_process]
                cmd  = "tar -cf " +tar_name +  " "+ "-C "+ os.path.dirname(src_folder) + " " + " ".join(elts_to_compress)
                run(cmd, False, False)
                with open(os.path.join(self.communication_folder, "FINISH_" + str(self.process_id)), "w"):
                    pass
                final_tar_name =  src_folder+".tar"
                if self.leader:
                    while len(list(filter(lambda elt : elt[:7] == "FINISH_", os.listdir(self.cache_dir)))) != self.nb_process:
                        time.sleep(1)
                    with open(os.path.join(self.communication_folder, "WAIT"), "w"):
                        pass
                    tars_to_concatenate = [src_folder + i + ".tar" for i in range(self.nb_process)]
                    concatenate_tar_list(tars_to_concatenate, final_tar_name, buffer=int(1e9), remove_sub_tar = True)
                    # if os.path.normpath(src_folder) == os.path.normcase(self.cache_dir):
                    #     # TODO do not do this, pick all the file and create a new folder with the correct name !
                    #     os.makedirs(os.path.join(self.cache_dir, self.root_renaming))
                    #     rename_tar = os.path.join(os.path.dirname(final_tar_name), self.root_renaming+".tar")
                    #     run("mv {} {}".format(final_tar_name, rename_tar), False, False)
                    #     final_tar_name = rename_tar 
                    run("mv {}  {}".format(final_tar_name, dst_folder), False, False) 
                    run("rm {}".format(os.path.join(self.communication_folder, "WAIT")), False, True, True)
                    time.sleep(2)
                    # run("rm {}".format(os.path.join(self.cache_dir, "READY_*")), False, True, True)
                else:
                    while  not(os.path.exists(final_tar_name)):
                        time.sleep(1)
                    while os.path.exists(os.path.join(self.communication_folder, "WAIT")):
                        time.sleep(1)
            return 
        
        if self.leader:
            print("saving cache...", flush = True)
            while len(list(filter(lambda elt : elt[:5] == "READY", os.listdir(self.communication_folder)))) != self.nb_process:
                time.sleep(1)
            run("rm {}".format(os.path.join(self.communication_folder, "READY_*")), False, True, True)
            for (src_folder, dst_folder) in self.folder_to_save:
                print("dealing with ", src_folder, " to ", dst_folder,flush=True)
                try:
                    file_to_remove_list = list(filter(lambda elt: elt[:22] == "UNHOLDFOLDEREXTRACTION", os.listdir(self.communication_folder)))
                    for file in file_to_remove_list:
                        os.remove(os.path.join(self.communication_folder, file))
                except Exception:
                    pass
                if os.path.normpath(src_folder) == os.path.normpath(self.cache_dir):
                        print("dealing with root folder", flush=True)
                        # TODO do not do this, pick all the file and create a new folder with the correct name !
                        os.makedirs(os.path.join(self.cache_dir, self.root_renaming))
                        src_folder = os.path.join(self.cache_dir, self.root_renaming)
                        print("dealing with ", src_folder, " to ", dst_folder,flush=True)
                        print("mv {} {}".format(os.path.join(self.cache_dir, "*"), src_folder), flush=True)
                        try:
                            run("mv {} {}".format(os.path.join(self.cache_dir, "*"), src_folder), False, True, True)
                        except Exception as e:
                            print(e)
                print("current content size is ", len(os.listdir(src_folder)), flush=True)
                src_folder = src_folder[:-1] if src_folder[-1] == "/" else src_folder
                compress_to_tar(src_folder, replace_existing=True,remove_init_folder=True)
                print("cache content ", run("ls -lthr " + self.cache_dir + " | wc -l", False, True, True), flush=True)
                # if self.save_dir and format_prepath(src_folder) == format_prepath(self.cache_link) :
                #     new_name = os.path.join("/".join(src_folder.split("/") [:-1]), (self.save_dir[:-1] if self.save_dir[-1] == "/" else self.save_dir) + ".tar")
                #     run("mv {}  {}".format(src_folder+".tar", new_name), False, False) 
                #     tar_path = new_name
                # else:
                tar_path = src_folder + ".tar"
                # if os.path.normpath(src_folder) == os.path.normcase(self.cache_dir):
                #     rename_tar = os.path.join(os.path.dirname(tar_path), self.root_renaming+".tar")
                #     run("mv {} {}".format(tar_path, rename_tar), False, False)
                #     tar_path = rename_tar 
                print("tar path is ", tar_path, flush=True)
                run("mv {} {}".format(tar_path, dst_folder), False, True, True) 
            print("cache saved")


    
    def move_and_extract_folder(self, src_path:str, dest_relative_path = "", copy:bool =True, extract_at_root:bool=True, is_file=False):
        """
        Will move the specifier folder/file to the cache. If the path points to a tar file, the tar file will be extracted within the cache 
        INPUT:
        - src_path: path toward a folder or a tar file 
        - copy: if set to False, the folder will be moved
        - extract_at_root: if set to True will move the extracted tar content to the root

        Returns the resulting folder path
        """
        if self.debugging:
            return src_path
        if not(src_path [-4:] == ".tar") and not(is_file):
            src_path = format_prepath(src_path)[:-1]
        if self.leader:
            if dest_relative_path:
                resulting_folder_path= os.path.join( self.cache_dir,dest_relative_path, src_path.split("/")[-1].split(".tar")[0] )
            else:
                resulting_folder_path= os.path.join( self.cache_dir,src_path.split("/")[-1].split(".tar")[0] )
        else:
            if dest_relative_path:
                resulting_folder_path= os.path.join( self.cache_link,dest_relative_path,src_path.split("/")[-1].split(".tar")[0] )
            else:
                resulting_folder_path= os.path.join( self.cache_link,src_path.split("/")[-1].split(".tar")[0] )

        unholder_path = os.path.join(self.communication_folder, f"UNHOLDFOLDEREXTRACTION_{src_path.replace('/', '-')}")
        if not(self.leader):
            if extract_at_root:
                assert not(self.root_renaming), "more than one extraction at root level"
                self.root_renaming = os.path.basename(resulting_folder_path)
            while not(os.path.exists(unholder_path)):
                time.sleep(5)
                self.check_and_reraise_raised_error()
            self.check_and_reraise_raised_error()
            return self.cache_link if extract_at_root else resulting_folder_path   
        try:
            if self.check_raised_error():
                raise FileExistsError(f"old error file detected {self.error_file}")
            dest_path = os.path.join(self.cache_dir, dest_relative_path)
            os.makedirs(dest_path, exist_ok=True)
            if copy:
                run("rsync -ah --progress {}  {}".format(src_path, dest_path), False, False)        
            else:
                run("mv {}  {}".format(src_path,  os.path.join(self.cache_dir, dest_path)), False, False)
            if src_path[-4:] == ".tar":
                tar_name  = os.path.basename(src_path)
                print("extracting ", os.path.join(dest_path, tar_name), flush = True)
                extracts_tar(os.path.join(dest_path, tar_name), remove_init_tar_folder=True)
                print("content is then ", run("ls " + dest_path , False, False), flush=True)
            if extract_at_root:
                assert os.path.isdir(resulting_folder_path), f"{src_path} is not a folder"
                assert not(self.root_renaming), "more than one extraction at root level"
                self.root_renaming = os.path.basename(resulting_folder_path)
                print("extracting  at root", flush =True)
                if len(os.listdir(resulting_folder_path)) > 0:
                    run("mv {} {}".format(os.path.join(resulting_folder_path, "*"), self.cache_dir), False, True, True)
                else:
                    print(f"warning {src_path} is empty", flush=True)
                run("rm -d {}".format(resulting_folder_path), False, False)
            with open(unholder_path, "w"):
                pass
            return self.cache_dir if extract_at_root else resulting_folder_path
        except Exception as e:
            self.create_error_file()
            raise e
        


    def __del__(self):
        if self.debugging:
            return
        if self.leader:
            print("saving folder to be saved", flush=True)
        self.save()
        
        if self.leader:
            print("deleating cache", flush=True)
            try:
                run("rm -rf {}".format(os.path.normpath(self.cache_dir)), False, True, True)
            except Exception as e:
                print(f"fail to delete {os.path.normpath(self.cache_dir)}", flush=True)
            print("deleting syminlk", flush=True)
            try:
                run("rm {}".format(os.path.normpath(self.cache_link)), False, True, True)
            except Exception as e:
                print(f"fail to delete {os.path.normpath(self.cache_link)}", flush=True)
            print("deleting communication folder", flush=True)
            try:
                run("rm -rf {}".format(os.path.normpath(self.communication_folder)), False, True, True)
            except Exception as e:
                print(f"fail to delete {os.path.normpath(self.communication_folder)}", flush=True)
            assert not(os.path.exists(os.path.normpath(self.cache_dir)))
            time.sleep(2)
        else:
            while os.path.exists(self.cache_link):
                self.check_and_reraise_raised_error()
                time.sleep(1)


        